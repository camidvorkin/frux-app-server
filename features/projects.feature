Feature: projects

  Scenario: a new project is created
    Given a new project
      And user with mail "johndoe@gmail.com" is authenticated
      When user create a project "Environment Project"
      And is about "Plant a tree"
      And the category is "ART"
      And the stage is "COMPLETE"
      And hashtags "#planet,#green"
      And the total amount to be collected is 5000
      Then the project "Environment Project", description "Plant a tree", category "ART", stage "COMPLETE" and goal 5000 is created correctly

  Scenario: a project with no category is set as "OTHERS"
     Given a new project
      And user with mail "johndoe@gmail.com" is authenticated
      When user create a project "Tech Project"
      And is about "Computer engineering"
      And the stage is "IN_PROGRESS"
      And hashtags "#python"
      And the total amount to be collected is 5000
      Then the project "Tech Project", description "Computer engineering", category "OTHERS", stage "IN_PROGRESS" and goal 5000 is created correctly

  Scenario: a project with no stage it just started
     Given a new project
      And user with mail "johndoe@gmail.com" is authenticated
      When user create a project "Music Project"
      And is about "Create a short clip"
      And the category is "MUSIC"
      And hashtags "#guitar,#rock,#music"
      And the total amount to be collected is 2000
      Then the project "Music Project", description "Create a short clip", category "MUSIC", stage "IN_PROGRESS" and goal 2000 is created correctly

  Scenario: list projects
     Given user with mail "johndoe@gmail.com" is authenticated
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
      When user create a project "Movie Project"
      And is about "Create a horror movie"
      And the category is "MOVIE"
      And the total amount to be collected is 10000
      Then operation is rejected with the message "Invalid Category! Try with:SPORTS,ART,MUSIC,OTHERS"

  Scenario: find project by id
     Given user with mail "johndoe@gmail.com" is authenticated
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
