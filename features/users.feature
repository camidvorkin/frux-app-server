Feature: users

  Scenario: a new user is registered
     Given user is not registered
      When user registers with username "pepe", name "Pepe", lastname "Suarez" and mail "pepe@fi.uba.ar"
      And image "image1" with location "-34.588363,-58.423254" and address "Urquiza"
      Then user already registered with username "pepe" and mail "pepe@fi.uba.ar"

  Scenario: user registers with an already used email
     Given user is already registered with mail "pepe@fi.uba.ar"
      When user registers with username "pepe", name "Pepe", lastname "Suarez" and mail "pepe@fi.uba.ar"
      And image "image1" with location "-34.588363,-58.423254" and address "Urquiza"
      Then operation is rejected with the message "Email address already registered!"

  Scenario: register with an invalid email
     Given user is not registered
      When user registers with username "pepe", name "Pepe", lastname "Suarez" and mail "pepe"
      And image "image1" with location "-34.588363,-58.423254" and address "Urquiza"
      Then operation is rejected with the message "Invalid email address!"

  Scenario: list users
     Given user is already registered with mail "pepe@fi.uba.ar"
       And user is already registered with mail "andrea@fi.uba.ar"
      When users are listed
      Then get a list of 2 users

  Scenario: find user by id
     Given user is already registered with mail "pepe@fi.uba.ar"
      And user is already registered with mail "andrea@fi.uba.ar"
      When user with id 1 is listed
      Then get user with mail "pepe@fi.uba.ar"

  Scenario: update user information
     Given user is already registered with mail "pepe@fi.uba.ar"
      When user update their username to "Pepito" and their image to "image7"
      Then the user's information change

   Scenario: a new user is registered with default values
     Given user is not registered
      When user registers with username "pepito", name "Pepe", lastname "Suarez" and mail "pepe@fi.uba.ar"
      And image "image1" with location "-34.588363,-58.423254" and address "Urquiza"
      Then user already registered with description "" and no role
