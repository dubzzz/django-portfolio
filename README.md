# django-portfolio

## Project

PortFolio developed using Django Framework (version 1.4.5). Its aim is to be able to show some of your main projects to the world easily.

## Make it work

### Setup your Django installation

+ On Debian: use apt to install the package **python-django**
+ Otherwise: refer to [Django Framework official documentation](https://www.djangoproject.com/download/)

### Get the latest development version

```bash
git clone https://github.com/dubzzz/django-portfolio.git
```
Or get the [zipball from GitHub repository](https://github.com/dubzzz/django-portfolio/archive/master.zip).

### Setup the project

+ Copy the file **django-portfolio/PortFolio/PortFolio/settings.py.sample** to **django-portfolio/PortFolio/PortFolio/settings.py**
+ Run the script **generate_new_secret_key.py** to generate a SECRET_KEY for the project
+ Edit settings.py

### Test it, run it

For tests, you just have to run the command:
```bash
python manage.py syncdb # Generate the database
python manage.py runserver 0.0.0.0:8000 # Run the development server
```

For more details concerning how to run this project using an Apache server please have a look to [Django Framework official documentation](https://www.djangoproject.com/download/).

## How does it look like?

[My PortFolio](http://portfolio.dubien.me/)
