# AI-Assisted Development Documentation

## 1. Overview

Artificial intelligence tools were used as development assistants throughout the development of the Student Information Management REST API. AI was used to support coding, debugging, testing, documentation, and understanding of framework concepts.

The developer remained responsible for reviewing, modifying, executing, and validating the generated or suggested solutions.

## 2. Areas Where AI Was Used

### Code Development

AI assistance was used to help develop and refine components of the REST API, including:

* FastAPI route implementation
* SQLAlchemy models and database relationships
* Pydantic schemas
* Authentication and JWT handling
* CRUD operations
* Input validation
* Database queries
* API response handling

### Database Development

AI was used to assist with:

* Designing database relationships
* Creating SQLAlchemy model structures
* Understanding foreign-key relationships
* Developing and reviewing Alembic migrations
* Creating database seed data
* Generating demonstration records required for the laboratory activity

### Debugging

AI was used to help investigate errors encountered during development and API testing.

Examples included:

* Database constraint errors
* Validation errors
* Authentication issues
* Incorrect API requests
* Partial-update behavior
* Foreign-key and referential-integrity issues

The suggested solutions were tested against the actual application before being accepted.

### Testing

AI assistance was used to:

* Identify test scenarios
* Generate or refine automated test cases
* Review expected API behavior
* Interpret test failures
* Suggest validation and edge cases

The completed automated test suite was executed locally and produced:

**33 passed**

API functionality was also manually tested using Postman and Swagger UI.

### Documentation

AI was used to assist with:

* README preparation
* API documentation organization
* Project documentation
* Test documentation
* Explaining technical concepts
* Organizing the final laboratory deliverables

## 3. AI-Assisted Workflow

The general development workflow was:

1. Identify a required API feature or problem.
2. Use AI to understand possible implementation approaches.
3. Generate or refine code with AI assistance.
4. Review the suggested implementation.
5. Apply the implementation to the project.
6. Run the API and automated tests.
7. Test the functionality through Swagger or Postman.
8. Investigate and correct errors when necessary.
9. Validate the final behavior manually.

AI suggestions were treated as development assistance rather than automatically accepted code.

## 4. Human Validation

All important AI-assisted outputs were reviewed and tested by the developer.

Validation included:

* Running the FastAPI server
* Running automated tests
* Performing API requests through Postman
* Checking Swagger/OpenAPI documentation
* Verifying database records
* Testing validation and error responses
* Reviewing generated code and modifying it when necessary

This helped ensure that the final implementation reflected the actual behavior of the application.

## 5. Examples of AI Contribution

Examples of tasks where AI assistance was useful include:

| Task            | AI Contribution                                       | Human Validation                     |
| --------------- | ----------------------------------------------------- | ------------------------------------ |
| API structure   | Suggested FastAPI organization                        | Reviewed and executed project        |
| Database models | Assisted with SQLAlchemy relationships                | Verified against database behavior   |
| Authentication  | Assisted with JWT and password hashing implementation | Tested login and protected endpoints |
| CRUD endpoints  | Assisted with route and database logic                | Tested through Postman               |
| Seed data       | Assisted in creating required demonstration records   | Verified record counts               |
| Automated tests | Assisted with test scenarios and implementation       | Executed test suite                  |
| Debugging       | Helped interpret errors and suggest fixes             | Tested fixes against the actual API  |
| Documentation   | Assisted in organizing project documentation          | Reviewed final content               |

## 6. Limitations and Developer Responsibility

AI-generated suggestions were not assumed to be correct. Some suggestions required modification or additional debugging before they worked correctly with the project.

The developer was responsible for:

* Final code decisions
* Database configuration
* Testing
* Reviewing AI-generated content
* Verifying API behavior
* Identifying incomplete functionality
* Reporting known limitations honestly

## 7. Summary

AI served as a development assistant throughout the project by reducing development time, helping interpret technical problems, and supporting implementation and testing. The final application was still validated through actual execution, automated tests, Swagger, Postman, and database verification.

The use of AI therefore formed part of an **AI-assisted development workflow**, while technical decisions and final validation remained the responsibility of the developer.
