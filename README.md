# Agdesk_Farm_Management
This repository provides the source code for AgDesk Farm Management, a web-based application designed to streamline and optimize farm operations.

# Getting Started
1. Software Dependencies
2. Setting up the Python Environment
3. Setting up a Database
4. Connecting the Database to Agdesk's Environment
5. Starting the Server and some Common Issues


# Software Dependencies

## PostgreSQL

### Downloading PostgreSQL
PostgreSQL is the relational database management system of choice for the Agdesk solution. The package can be downloaded at the following links.

https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

*_This guide assumes that PostGreSQL is being installed on a Windows x64 based operating environment_

Select the operating system family and architecture for which you intend to download the PostgreSQL package onto **Ensuring that version 16.4 is selected**. 

### Running the Installer

1. Select Next at the Welcome Screen
2. Specify the Installation Directory you wish to install the package to. By default, this should be C:\Program Files\PostgreSQL\16
3. Select Components: Ensure that all possible components are selected. **particularaly pgAdmin4 and Stack Builder configuration of these will occur later in this guide.**
4. Specify the directory at which you wish to install data for the PostgreSQL pacakge to. By default, this should be C:\Program Files\PostgreSQL\16\data
5. provide a password for the database superuser. **Store this password somewhere secure as you (and your team) will use it to access Agdesk's database.**
6. In most cases the default suggested port 5432 will suffice, however, this can be changed as required.
7. Unless specifically required - do not change the locale. By leaving it as [Default Local] it will match your device's operating system.
8. Take note of the pre-installation summary to confirm that everything has been configured correctly.
9. select "Next" and run the installer. After the installation has finished, a checkbox will appear prompting you to launch stack builder, **make sure this box is checked.**

### Running the Stackbuilder installer

1. At the first screen on the stack builder installer - select "PostgreSQL 16 (x64) on port 5432 (or your port) from the drop down menu.
2. A tree of options will appear at the next phase of installation. Expand the Database server option, then ensure that PostgreSQL (64 bit) v16.4-1 is checked. **Do not progress to the next page**
  **If this option says (installed) next to it, then you can leave it unchecked. **
3. Select the Spatial Extensions option and check the box called PostGIS 3.4.2 bundle for PostgreSQL 16 (64 bit) v3.4.2 **Progress to the next page after selecting this**
4. Ensure the selected packages to install are correct - The package download directory will be the currently signed in user by default.
   **If the installer stops responding after clicking next - WAIT. it may take some time, but will then resume with the install in a popup menu**
6. on the following menu, leave the option to skip installation unchecked and click next.
7. Accept the license agreement in the PostGIS Bundle popup window
8. On the Choose components menu, ensure that the following boxes are checked. Click Next
   -   PostGIS Bundle
   -   Register PROJ_LIB Env Variable
   -   Register GDAL_DATA Env Variable
   -   Enable Key GDAL Drivers
   -   Allow Out-db Rasters
   -   Register SSL Bundle
9. Set the install location of PostGIS. Installing it in the default listed directory is recommended for simplicity.
10. Select Close and Finish the installation.

## Installing Python

_This installation guide uses python version 3.12.0_

Begin by Downloading Python 3.12.0 from the following link https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe 
when you run the installer check the box to add Python 3.8 to PATH and check the box to Install Launcher for all users. Following this, select Install Now.
This Concludes the installation of Python 3.8

# Setting Up The Python Environment

## Create the Virtual Environment

To Begin adding to this repository, you will first need to create a virtual python environment in which all of the packages in requirements.txt will be installed.

Before running this run the below script in a powershell/terminal window.

```cmd
pip install virtualenv
```

Once virtualenv has completed installing, navigate to the project's root directory and perform the following.

```cmd
python3.8 -m venv env
```

This will create a folder called env inside of the project.
When ready to begin developing run the below commands

```cmd
env/Scripts/activate.bat //If running in CMD
env/Scripts/Activate.ps1 //If running in Powershell
```

The environment can be deactivated at a later point with the following commands.

```cmd
env/Scripts/deactivate.bat //If running in CMD
```

## Ensuring the Packages is Consistent

Viewing the currently installed packages is as simple as the list command.

```cmd
pip list
```

To make sure that the environment contains only the packages in requirements.txt, it can be useful to uninstall all the current packages before running the install command.
If pip list returns no packages, proceed to package installation.

```cmd
pip freeze > toberemoved.txt # Creates a text file of current packages, 
pip uninstall -r toberemoved.txt -y
```

## Install Required Packages to the Virtual Environment

Once the Virtual environment is running, the necessary python packages should be installed.
This can be performed by running the command pip install on the requirements file.
The file, requirements.txt, contains a list of all packages used in the project.

```cmd
pip install -r Agdesk_Farm_Management/Package_management/requirements.txt
```

Following this the Python Environment has been configured. However, the AgDesk Django evnironment still needs configuration.
Prior to doing this, a PostgreSQL database must be setup and connected to the AgDesk Environment.

# Setup the Database and Link it to AgDesks Environment

In the projects current state, it will not run as no database has been created or linked to the project.

## Creating the Database in PgAdmin 4

1. Open the PgAdmin 4 application and select the drop down option called servers from the left hand menu.
2. After selecting the option, you will need to enter the password that was configured for the super user in the PostgreSQL installation section.
3. Select the dropdown option called Databases, then right click it and select the Create option, followed by the Database option.
4. Enter a Database Title. It does not matter what this is, but it will be used in the project when linking AgDesk to the Database.
5. Finally, click Save.

A Database has now been created for Agdesk in the PgAdmin 4 app.


## Linking the Database to the AgDesk Project

Now return to settings.py in the AgDesk Django project and find the dictionary titled "DATABASES", It should show the below values by default.

```python
DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.sqlite3',
       'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
   }
}
```

This dictionary should be edited so that it reflects the below code, most values will need to replaced with their respective values for the current application.

```python
DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql',
       'NAME': ‘<database_name>’,
       'USER': '<database_username>',
       'PASSWORD': '<password>',
       'HOST': '<database_hostname_or_ip>',
       'PORT': '<database_port>',
   }
}
```

Once complete open the terminal which is running the Python virtual environment for AgDesk and execute the following commands in order.

```cmd
python manage.py makemigrations
```

```cmd
python manage.py migrate
```

Upon re-opening PgAdmin4, all of the models from Django should now have a tabular representation in the following directory <database_name> > Schemas > Tables.

## Running the Django Server

Confirm that the application works by running the following from the root directory of the project.

```cmd
py .\AgDeskDjango\manage.py runserver
```

# Useful Resources

Django Documentation: https://docs.djangoproject.com/en/5.1/

#
