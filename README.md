# PYTHON CODE OBJECT DISSASEMBLY REPORT GENERATOR
A python script that lets you generate bytecode object dissasembly report which contains all important informations about it. Everything wrapped in small IDLE-styled HTML file.
### USAGE
cmd:
```
py -m dis_report <module_name> <object_name> -o <output_file>
```
Where _object_name_ is the name of python object from which to retrieve code.
<br />
python:
```python
import dis_report

def your_function(foo):
	print(foo)

report = dis_report.generate_report_html(my_function.__code__)
```
Where _report_ variable is a complete HTML document that can be later written to a file and opened in browser.
