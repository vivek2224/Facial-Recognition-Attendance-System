FRAS-SR-PROJ

This is our facial recognition attendance application. In our application, Professors and Administrators can access classrooms and add or remove students. In order for a professor to use the system, an Administrator must create an account for them first. Then, professors can add images of the students which will later be used by the OpenCV algorithm to recognize and update their status to present. To use this application, some dependencies must be installed. First, the user must have Python 3.8. On top of that, users must install the following python dependencies: Flask, Flask-Mail, Jinja2, MarkupSafe, Pillow, PyMySQL, Wekzeug, bcrypt, blinker, cmake, dlib, face-recognition, numpy, opencv-python, pathlib, pygal, and requests

Then, users can run the main.py file which will generate a local url that can be pasted into any web browser. From here, the application can be used.

Here is a link to our application demo: https://youtu.be/mmdF1GMVPvs

The code structure is setup to use different API's built in Python. These API's allow the database to be updates and for improved code quality and reusability. Our entire project is based on Python for the backend, with HTML, CSS, and Jinja used for the frontend.