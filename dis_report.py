import dis
import html
import time
import types

import airium

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

def generate_report_html(code_obj: types.CodeType) -> str:
    start = time.perf_counter()

    co_name = code_obj.co_name
    co_filename = code_obj.co_filename

    doc = airium.Airium()
    doc('<!DOCTYPE html>')
    with doc.html(lang='en'):
        with doc.head():
            doc.meta(charset='utf-8')
            doc.title(_t='Dissasembly report')
            doc.link(rel='stylesheet', href='style.css')

        with doc.body():
            doc.h3(id='title', _t='DISASSEMBLY REPORT OF OBJECT')
            doc.h1(id='obj_name', _t=co_name)
            doc.br()

            with doc.div(id='info'):
                doc('NAME: ')
                doc.span(klass='attrib', _t=co_name)
                doc.br()

                doc('FILEPATH: ')
                doc.a(klass='attrib', href=f'file:///{co_filename}', _t=co_filename)
                doc.br()

                doc('COMPILER FLAGS: ')
                flags = dis.pretty_flags(code_obj.co_flags).split(', ')
                with doc.span(klass='attrib'):
                    for flag in flags:
                        desc = _FLAGS_DESCRPTIONS.get(flag, None)
                        if desc is None:
                            doc(html.escape(flag))
                        else:
                            doc.span(title=html.escape(desc), _t=html.escape(flag))

                doc.br()

                doc('STACK SIZE: ')
                doc.span(klass='attrib', _t=str(code_obj.co_stacksize))
                doc.br()

            doc.hr()

            doc.span(klass='header', _t='Constants')
            with doc.table():
                with doc.thead().tr():
                    doc.th(_t='INDEX')
                    doc.th(_t='VALUE')
                    doc.th(_t='TYPE')

                with doc.tbody():
                    for i, val in enumerate(code_obj.co_consts):
                        with doc.tr():
                            doc.td(_t=str(i))
                            doc.td(_t=html.escape(repr(val)))
                            doc.td(_t=html.escape(type(val).__name__))

            doc.hr()

            doc.span(klass='header', _t='Variables')
            with doc.table():
                with doc.thead().tr():
                    doc.th(_t='INDEX')
                    doc.th(_t='NAME')

                with doc.tbody():
                    for i, name in enumerate(code_obj.co_varnames):
                        with doc.tr():
                            doc.td(_t=str(i))
                            doc.td(_t=name)

            doc.hr()

            doc.span(klass='header', _t='Bytecode')
            with doc.table():
                with doc.thead().tr():
                    doc.th(_t='LINE')
                    doc.th(_t='OP NUMBER')
                    doc.th(_t='OPCODE')
                    doc.th(_t='ARGUMENT', colspan=2)

                with doc.tbody():
                    for inst in dis.get_instructions(code_obj):
                        with doc.tr():
                            with doc.td():
                                if inst.starts_line is not None:
                                    doc.span(klass='lineno', _t=str(inst.starts_line))

                            with doc.td():
                                if inst.is_jump_target:
                                    with doc.span(id=f'jump_{inst.offset}'):
                                        doc.u(_t=str(inst.offset))
                                else:
                                    doc(str(inst.offset))

                            with doc.td():
                                doc.span(klass='opcode', _t=inst.opname)

                            if inst.arg is not None:
                                doc.td(_t=str(inst.arg))

                                with doc.td():
                                    arg_repr = html.escape(inst.argrepr)

                                    if inst.argrepr.startswith('to '):
                                        doc.a(klass='value', href=f'#jump_{inst.argval}', _t=arg_repr)
                                    else:
                                        doc.span(klass='value', _t=arg_repr)

            doc.hr()
            doc.h3(id='title', _t='END OF REPORT')

    print(f'Report document generated in {time.perf_counter() - start} seconds.')

    return str(doc)

if __name__ == '__main__':
    with open('result.html', 'w+') as f:
        f.write(generate_report_html(generate_report_html.__code__))
