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

  Scenario: update username and image
     Given user is already registered with mail "pepe@fi.uba.ar"
      When user updates their username to "Pepito" and their image to "image7"
      Then the user's username changes to "Pepito" and their image changes to "image7"

  Scenario: update user location
     Given user is already registered with mail "pepe@fi.uba.ar"
      When user updates their latitude to "-34.588363" and longitude to "-58.423254"
      Then the user's latitude changes to "-34.588363" and longitude to "-58.423254"

   Scenario: a new user is registered with default values
     Given user is not registered
      When user registers with username "pepito", name "Pepe", lastname "Suarez" and mail "pepe@fi.uba.ar"
      And image "image1" with location "-34.588363,-58.423254" and address "Urquiza"
      Then user already registered with description "" and no role

   Scenario: a new user tries to register with invalid location
     Given user is not registered
      When user registers with username "pepito", name "Pepe", lastname "Suarez" and mail "pepe@fi.uba.ar"
      And image "image1" with location "-3400.588363,-528.423254" and address "Urquiza"
      Then operation is rejected with the message "Invalid location!"

   Scenario: a new user registers with defined interests
     Given user is not registered
      And default categories are in the database
      When user registers with username "pepito", name "Pepe", lastname "Suarez" and mail "pepe@fi.uba.ar"
      And interests "Games,Film"
      And image "image1" with location "-34.588363,-58.423254" and address "Urquiza"
      Then registration is successful

   Scenario: a new user registers with an invalid interest
     Given user is not registered
      When user registers with username "pepito", name "Pepe", lastname "Suarez" and mail "pepe@fi.uba.ar"
      And interests "Opera"
      And image "image1" with location "-34.588363,-58.423254" and address "Urquiza"
      Then operation is rejected with the message "Invalid Category!"

  Scenario: update user's interests
     Given user is already registered with mail "pepe@fi.uba.ar"
      And default categories are in the database
      When user updates their interests to "Games,Film"
      Then the user's new interests are "Games,Film"

  Scenario: update user's interests twice
     Given user is already registered with mail "pepe@fi.uba.ar"
      And default categories are in the database
      When user updates their interests to "Games,Film"
      When user updates their interests to "Film,Music"
      Then the user's new interests are "Film,Music"

  Scenario: update user's interests with an invalid category
     Given user is already registered with mail "pepe@fi.uba.ar"
      When user updates their interests to "Games,Worlds"
      Then operation is rejected with the message "Invalid Category!"

   Scenario: user register as a Seer
     Given user is already registered with mail "pepe@fi.uba.ar"
      When user with mail "pepe@fi.uba.ar" has a seer role
      Then there is 1 seer in the system

   Scenario: user register as a Seer and then reject the position
     Given user is already registered with mail "pepe@fi.uba.ar"
      When user with mail "pepe@fi.uba.ar" has a seer role
      And user with mail "pepe@fi.uba.ar" reject the role as seer
      Then there is 0 seer in the system
