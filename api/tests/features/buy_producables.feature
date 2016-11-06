Feature: User 1 attempts to buy a producable 
    Scenario: You have enough money
        Given The system is set up properly
        Then I make sure that the inventory is empty
        Then I make sure that I have enough money
        Then I buy the producables 1
        Then I should get a 200 response
        And my inventory should contain producable 1

     Scenario: You dont have enough money
        Given The system is set up properly
        Then I make sure that the inventory is empty
        Then I spend all my money
        Then I buy the producables 1
        Then I should get a 409 response
        And my inventory should not contain producable 1
