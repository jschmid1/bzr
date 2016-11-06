Feature: Query for all 'basegoods'
    Scenario: Retrieve all items
        Given some basegoods are in the system
        Then I retrieve all basegoods
        Then I should get a 200 response
        And I should get a list of basegoods
