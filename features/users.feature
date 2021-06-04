Feature: users

  Scenario: a new user is registered
     Given user is not registered
      When user registers with name "Pepe Suarez" and mail "pepe@fi.uba.ar"
      Then user already registered with name "Pepe Suarez" and mail "pepe@fi.uba.ar"

  Scenario: user registers with an already used email
     Given user is already registered with name "Pepe Suarez" and mail "pepe@fi.uba.ar"
      When user registers with name "Pepe Suarez" and mail "pepe@fi.uba.ar"
      Then operation is rejected with the message "Email address already registered!"

  Scenario: register with an invalid email
     Given user is not registered
      When user registers with name "Pepe Suarez" and mail "pepe"
      Then operation is rejected with the message "Invalid email address!"

  Scenario: list users
     Given user is already registered with name "Pepe Suarez" and mail "pepe@fi.uba.ar"
       And user is already registered with name "Andrea Suarez" and mail "andrea@fi.uba.ar"
      When users are listed
      Then get a list of 2 users

  Scenario: find user by id
     Given user is already registered with name "Pepe Suarez" and mail "pepe@fi.uba.ar"
       And user is already registered with name "Andrea Suarez" and mail "andrea@fi.uba.ar"
      When user with id 1 is listed
      Then get user with name "Pepe Suarez" and mail "pepe@fi.uba.ar"

  Scenario: update user information
     Given user is already registered with name "Pepe Suarez" and mail "pepe@fi.uba.ar"
      When user update their username to "Pepito" and their mail to "pepito@fi.uba.ar"
      Then the user's information change
