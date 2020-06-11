## search hospital happy path
* greet
  - utter_greet
* search_provider{"facility_type":"hospital", "location":"San Francisco"}
  - action_facility_search
  - slot{"address":"300 Hyde St, San Francisco"}
* thanks
  - utter_goodbye

## search hospital + location
* greet
  - utter_greet
* search_provider{"facility_type":"hospital"}
  - utter_ask_location
* inform{"location":"San Francisco"}
  - action_facility_search
* thanks
  - utter_goodbye

## happy path
* greet
  - utter_greet
* mood_great
  - utter_happy

## feeling path

* feeling
  - utter_feeling

## sad path 1
* greet
  - utter_greet
* mood_unhappy
  - utter_cheer_up
  - utter_did_that_help
* affirm
  - utter_happy

## sad path 2
* greet
  - utter_greet
* mood_unhappy
  - utter_cheer_up
  - utter_did_that_help
* deny
  - utter_goodbye

## say goodbye
* goodbye
  - utter_goodbye

## provide name
* name
  - utter_name
  - utter_how_can_i_help

## purpose

* purpose
  - utter_purpose

## ask for help

* help
  - utter_name
  - utter_how_can_i_help

## bot challenge
* bot_challenge
  - utter_iamabot


