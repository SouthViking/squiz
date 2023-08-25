<div id="header" align="center">
  <img src="https://media.giphy.com/media/xTiN0IuPQxRqzxodZm/giphy.gif" width="400"/>

<h1>
  Squiz
</hi>
  
</div>

---

## 💭 What is Squiz?

Squiz is an API that allows to create and solve quizzes. These quizzes can be scheduled and defined to be answered within a specific range of time.
The API was built using the Django framework with help of the Graphene library to support GraphQL queries and mutations. It connects to a MySQL database by using the default ORM interface provided by Django.

## 📁 Project structure

The API follows the default structure generated by Django, which separates the logic into the following "applications":

- ❓ **Quizzes**: Contains all the business logic related to the **main entities of the project**, which are: **quiz, question and option**.

<br>

- 👥 **Users**: Contains all the business logic related to the **users** and the registration/authentication process to use the API.

<br>

- 📅 **Scheduler**: Contains all the business logic related to the global **scheduler** of the app. The scheduler allows to automatically enable and disable quizzes based on their start and end time. It can also execute background time based tasks.


📁 In general, these applications share a well defined structure which is composed of the following sub-folders:

- **Migrations**: Contains auto-generated history files about the changes made to the database schema. These changes allow to build the DB in a fresh DBMS by executing the Django command `python3 manage.py migrate` (See more detail in the installation and execution section).

- **Mutators**: Contains the definition of the mutators that will be registered in the app. These mutators are then imported in the main GraphQL schema definition. 

- **Queries**: Similar to the mutators, this folder contains all the definition of the queries that can be used. They are also imported and registered in the main GraphQL schema object.

- **Tests**: This folder contains different tests related to its application.

📰 Also, the following files can be found in the applications folders:

- **Jobs**: Defines the jobs that will be added to the scheduler. They expose an `initial_jobs_config` variable containing the different jobs that should be registered. They can be of interval or time based types. The jobs get registered when the application gets executed.

- **Models**: Contains the ORM definition of the tables in the database. The classes allow to interact with the database by using the ORM interface.

- **Schema**: Contains the aggregation of all the queries and mutations of the application. It is a common file that gets imported and added to the core schema definition.

- **Utils**: Contains any kind of utility function related to the application.

- **Validators**: Contains validation functions that will run for specific database attributes when the ORM detects that data is being saved.

ℹ️ For any further information about the default folders and files generated by the Django framework, please take a look at the official documentation.


## ⚙️ How to execute the project

### TODO 