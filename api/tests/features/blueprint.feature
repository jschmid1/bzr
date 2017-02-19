Feature: What is needed for the producable
    Scenario: Query a producable for its basegoods
        Given The system is set up properly 
        Then I ask for the blueprint of the producables 1
        Then I should get a 200 response
        And I see a list of basegoods in producable
