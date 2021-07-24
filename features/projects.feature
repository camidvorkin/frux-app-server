Feature: projects

  Scenario: a new project is created
    Given a new project
      And user with mail "johndoe@gmail.com" is authenticated
      And default categories are in the database
      When user create a project "Environment Project"
      And is about "Plant a tree"
      And the category is "Arts"
      And hashtags "#planet,#green"
      And the total amount to be collected is 5000
      Then the project "Environment Project", description "Plant a tree", category "Arts", state "CREATED" and goal 0 is created correctly

  Scenario: a project with no category is set as "Other"
     Given a new project
      And user with mail "johndoe@gmail.com" is authenticated
      And default categories are in the database
      When user create a project "Tech Project"
      And is about "Computer engineering"
      And hashtags "#python"
      And the total amount to be collected is 5000
      Then the project "Tech Project", description "Computer engineering", category "Other", state "CREATED" and goal 0 is created correctly

  Scenario: a project with no state it just started
     Given a new project
      And user with mail "johndoe@gmail.com" is authenticated
      And default categories are in the database
      When user create a project "Music Project"
      And is about "Create a short clip"
      And the category is "Music"
      And hashtags "#guitar,#rock,#music"
      And the total amount to be collected is 2000
      Then the project "Music Project", description "Create a short clip", category "Music", state "CREATED" and goal 0 is created correctly

  Scenario: list projects
     Given user with mail "johndoe@gmail.com" is authenticated
      And default categories are in the database
      And project "Teaching Football Program" has already been created for user
      And is about "Teaching kids to play football"
      And the total amount to be collected is 200
      And project "Teaching Tennis Program" has already been created for user
      And is about "Teaching kids to play tennis"
      And the total amount to be collected is 400
      When projects are listed
      Then get a list of 2 projects

  Scenario: search project by name
     Given user with mail "johndoe@gmail.com" is authenticated
      And default categories are in the database
      And project "Teaching Football Program" has already been created for user
      And is about "Teaching kids to play football"
      And the total amount to be collected is 200
      And project "Teaching Tennis Program" has already been created for user
      And is about "Teaching kids to play tennis"
      And the total amount to be collected is 400
      When projects are listed filtering by name "Teaching Tennis Program"
      Then get a list of 1 projects

  Scenario: Create a new project with invalid category
     Given a new project
      And user with mail "johndoe@gmail.com" is authenticated
      And default categories are in the database
      When user create a project "Movie Project"
      And is about "Create a horror movie"
      And the category is "My movie"
      And the total amount to be collected is 10000
      Then operation is rejected with the message "Invalid Category!"

  Scenario: find project by id
     Given user with mail "johndoe@gmail.com" is authenticated
      And default categories are in the database
      And project "Teaching Football Program" has already been created for user
      And is about "Teaching kids to play football"
      And the total amount to be collected is 200
      When project with id 1 is listed
      Then get project with name "Teaching Football Program" and description "Teaching kids to play football"

  Scenario: update a project
     Given an old project
      When project new name is "New project"
      And project new description is "Update old project"
      Then the project's information change


   Scenario: a project in "in progress" stage cannot have its funds withdrawn
    Given user with mail "johndoe@gmail.com" is authenticated and has a wallet
    And a new project was created by the user with title "Potato salad"
    And a stage was created with title "My first potato salad" and goal 150
    And a stage was created with title "My second potato salad" and goal 100
    And user with mail "ale@gmail.com" is authenticated and has a wallet
    And user with mail "ale@gmail.com" has a seer role
    When the owner of the project "johndoe@gmail.com" enables the project for funding
    And the seer of the project is "ale@gmail.com"
    And user with mail "ale@gmail.com" reject the role as seer
    Then operation is rejected with the message "Seer must wait until all their projects are either completed or cancelled! You can't leave the job in funding state"

   Scenario: cancel project
    Given an old project
    When the project is cancelled
    Then the stage of the project is "CANCELED"

   Scenario: a project in "canceled" stage can have its funds withdrawn
    Given user with mail "johndoe@gmail.com" is authenticated and has a wallet
    And a new project was created by the user with title "Potato salad"
    And a stage was created with title "My first potato salad" and goal 150
    And a stage was created with title "My second potato salad" and goal 100
    And user with mail "ale@gmail.com" is authenticated and has a wallet
    And user with mail "ale@gmail.com" has a seer role
    When the owner of the project "johndoe@gmail.com" enables the project for funding
    And the seer of the project is "ale@gmail.com"
    And the project is cancelled
    And user with mail "ela@gmail.com" is authenticated and has a wallet
    And user with mail "ela@gmail.com" has a seer role
    And user with mail "ale@gmail.com" reject the role as seer
    Then the seer of the project is "ela@gmail.com"
