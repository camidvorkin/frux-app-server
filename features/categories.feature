Feature: categories

  Scenario: list default categories
    Given default categories are in the database
      When categories are listed
      Then get a list of 9 categories

