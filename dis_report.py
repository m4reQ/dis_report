import dis
import html
import io
import os
import time
import types
import typing as t

_MAX_REPR_LEN = 64

_FLAGS_DESCRPTIONS = {
    'OPTIMIZED': 'The code object is optimized, using fast locals.',
    'NEWLOCALS': 'If set, a new dict will be created for the frame\'s f_locals when the code object is executed.',
    'VARARGS': 'The code object has a variable positional parameter (*args-like).',
    'VARKEYWORDS': 'The code object has a variable keyword parameter (**kwargs-like).',
    'NESTED': 'The flag is set when the code object is a nested function.',
    'GENERATOR': 'The flag is set when the code object is a generator function, i.e. a generator object is returned when the code object is executed.',
    'NOFREE': 'The flag is set if there are no free or cell variables.',
    'COROUTINE': 'The flag is set when the code object is a coroutine function. When the code object is executed it returns a coroutine object. See PEP 492 for more details.',
    'ITERABLE_COROUTINE': 'The flag is used to transform generators into generator-based coroutines. Generator objects with this flag can be used in await expression, and can yield from coroutine objects. See PEP 492 for more details.',
    'ASYNC_GENERATOR': 'The flag is set when the code object is an asynchronous generator function. When the code object is executed it returns an asynchronous generator object. See PEP 525 for more details.'}

def _create_html_table(data: t.Iterable[t.Any], row_constructor: t.Callable[[t.Any, int], str]) -> str:
    return ''.join(row_constructor(x, i) for i, x in enumerate(data))

def _consts_row_constructor(val: t.Any, index: int) -> str:
    if isinstance(val, types.CodeType):
        url = f'#{html.escape(val.co_name)}'
        _repr = html.escape(val.co_name)
        return f'<tr>\n<td>{index}</td>\n<td><a href={url}>{_repr}</a></td>\n<td>{type(val).__name__}</td>\n</tr>\n'

    _repr = html.escape(repr(val))
    return f'<tr>\n<td>{index}</td>\n<td><a class="value">{_repr}</a></td>\n<td>{type(val).__name__}</td>\n</tr>\n'

def _vars_row_constructor(val: t.Any, index: int) -> str:
    return f'<tr>\n<td>{index}</td>\n<td>{html.escape(val)}</td>\n'

def _instruction_row_constructor(inst: t.Any, _) -> str:
    if not isinstance(inst, dis.Instruction):
        raise TypeError('inst agrgument must be of type dis.Instruction.')

    res = io.StringIO()
    write = res.write
    write('<tr>\n')

    if inst.starts_line:
        write(f'<td><a class="lineno">{inst.starts_line}</a></td>\n')
    else:
        write('<td></td>\n')

    write(f'<td>')

    if inst.is_jump_target:
        write(f'<a id=jump_{inst.offset}><u>{inst.offset}</u></a>\n')
    else:
        write(f'{inst.offset}')

    write(f'</td>\n<td><a class="opcode">{inst.opname}</a></td>\n')

    if inst.arg:
        write(f'<td>{inst.arg}</td>\n<td><a class="value"')

        if inst.argrepr.startswith('to '):
            res.write(f' href=#jump_{inst.argval}')

        write(f'>({html.escape(inst.argrepr)})</a></td>\n')
    else:
        write('<td></td>\n<td></td>\n')

    write('</tr>\n')

    return res.getvalue()

def _create_html_flags_text(code_obj: types.CodeType) -> str:
    flags = dis.pretty_flags(code_obj.co_flags).split(', ')

    result = io.StringIO()
    for flag in flags:
        desc = _FLAGS_DESCRPTIONS.get(flag, None)
        if desc is None:
            result.write(f'{html.escape(flag)}, ')
        else:
            result.write(f'<span title="{html.escape(desc)}">{html.escape(flag)}</span>, ')

    return result.getvalue().removesuffix(', ')

def generate_report_html(code_obj: types.CodeType) -> str:
    start = time.perf_counter()
    fp = os.path.join(os.path.split(__file__)[0], 'template.html')
    with open(fp) as f:
        template = f.read()

    doc = template % (
        code_obj.co_name,
        code_obj.co_name,
        code_obj.co_filename,
        code_obj.co_filename,
        _create_html_flags_text(code_obj),
        code_obj.co_stacksize,
        _create_html_table(
            code_obj.co_consts,
            _consts_row_constructor),
        _create_html_table(
            code_obj.co_names,
            _vars_row_constructor),
        _create_html_table(
            code_obj.co_varnames,
            _vars_row_constructor),
        _create_html_table(
            dis.get_instructions(code_obj),
            _instruction_row_constructor))

    print(f'Report document generated in {time.perf_counter() - start} seconds.')

    return doc
