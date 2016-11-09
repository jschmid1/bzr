Feature: User 1 attempts to sell a basegood
#    Scenario: You have the basegood
#        Given The system is set up properly
#        Then I add the basegood 1 to my inventory
#        Then I sell the basegoods 1
#        Then I expect "sold" in the message 
#        Then I should get a 200 response

    Scenario: You dont have the basegood
        Given The system is set up properly
        Then I make sure that the inventory is empty
        Then I sell the basegoods 1
        Then I should get a 409 response
        Then I expect "You dont have what you want to sell" in the message 
