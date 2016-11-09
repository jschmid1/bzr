Feature: Query what you can do with a certain basegood
    Scenario: Query a basegood for its capabilities
        Given The system is set up properly 
        Then I ask for the capabilities of the basegoods 1
        Then I should get a 200 response
        And I see a nested list of producable in basegood
