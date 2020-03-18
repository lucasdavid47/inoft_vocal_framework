# Inoft Vocal Framework
 ## Create Alexa Skills, Google Actions and Samsung Bixby Capsules with the same codebase. In Python !

 #### The example do not show how to deploy the skill (in Lambda, API Gateway and the Javascript files for bixby). I'm soon going to make videos in french and english to explain how to use the framework, and deploy a skill accross platforms. Then a bit later on, there will be the CLI for auto-deployment, then the CMS, then the web interface, then the free cloud platform that will host everything for you while giving you access to everything, then the tools on the platform to collaborate between developpers and voice designers extremly efficiently. It's going to be great ;)

 #### This code makes an Alexa Skill, a Google Action and a Bixby Capsule, and its Pythonic !

 Hello World :
 ```
from inoft_vocal_framework import InoftSkill, InoftRequestHandler, InoftDefaultFallback

class LaunchRequestHandler(InoftRequestHandler):
   def can_handle(self) -> bool:
       return self.is_launch_request()

   def handle(self):
       self.say("Hello World !")
       return self.to_platform_dict()

class DefaultFallback(InoftDefaultFallback):
   def handle(self):
       self.say("I did not understand. Do you want me to say HELLO WORLD ?!")
       return self.to_platform_dict()

def lambda_handler(event, context):
   skill_builder = InoftSkill(disable_database=True)
   skill_builder.add_request_handler(LaunchRequestHandler)
   skill_builder.set_default_fallback_handler(DefaultFallback)
   return skill_builder.handle_any_platform(event=event, context=context)
 ```

 

## In depth tutorial

### The 3 classes :

All of the interactions with the framework are done inside of classes and their self object. You need to clearly understand their specificities. I recommand that you take the time to carefully read this section.

### InoftRequestHandler

This is the most basic class, it requires you to implement 2 functions

```
class LaunchRequestHandler(InoftRequestHandler):
    def can_handle(self) -> bool:
       return self.is_launch_request()
    
    def handle(self):
       self.say("Hello world ! Will you marry me ?")
       return self.to_platform_dict()
```

The can_handle function contain and return the result of the condition that will define if the handle function of the class, should create the response that will be send back to the vocal assistant.

And the handle function will create the response by using the self object, and return it with the to_platform_dict() function. You can of course call other functions, classes or handle functions from your handle function.

There is an aditionnal function you can use, which is handle_resume(self), that allow to automaticly resume an user to a point of the interaction. We will discover this in the advanced features.

### InoftStateHandler

```
class MarryMeStateHandler(InoftStateHandler):
    def handle(self):
        if YesHandler(self).can_handle():
            self.say("You said yes ? I love you !")
            return self.to_platform_dict()

        elif NoHandler(self).can_handle():
            self.say("What do you mean you said NO ?!!")
            return self.to_platform_dict()

    def fallback(self):
        self.say("Well, gotta make your choice, do you want to marry me or no ?")
        return self.to_platform_dict()
```

Weeeeell, i gotta explai

### InoftDefaultFallback

It is the last resort to handle any any fallback situation (where the user said or did something not supported by your interaction model). It will not override over the fallback method of a StateHandler class. It is really the last ressort.

You only have one function available, the handle function, like in the two other classes, you will interacte with the framework with the self object, and return with self.to_platform_dict()

```
class DefaultFallback(InoftDefaultFallback):
    def handle(self):
        self.say("You must be clear with what you want in life ! Otherwise i'm going to take"
        "replace you and take your programmer job that you love so much !")
        return self.to_platform_dict()
```

Having a InoftDefaultFallback class is required for every skill. Otherwise it will give you an exception.

### Putting the 3 classes together

 ```
from inoft_vocal_framework import InoftSkill, InoftRequestHandler, InoftStateHandler, InoftDefaultFallback

class LaunchRequestHandler(InoftRequestHandler):
    def can_handle(self) -> bool:
       return self.is_launch_request()
    
    def handle(self):
       self.say("Hello world ! Will you marry me ?")
       self.memorize_session_then_state(MarryMeStateHandler)
       return self.to_platform_dict()
       
class MarryMeStateHandler(InoftStateHandler):
    def handle(self):
        if YesHandler(self).can_handle():
            self.say("You said yes ? I love you !")
            return self.to_platform_dict()

        elif NoHandler(self).can_handle():
            self.say("What do you mean you said NO ?!!")
            return self.to_platform_dict()

    def fallback(self):
        self.say("Well, gotta make your choice, do you want to marry me or no ?")
        return self.to_platform_dict()

class DefaultFallback(InoftDefaultFallback):
    def handle(self):
        self.say("You must be clear with what you want in life ! Otherwise i'm going to take"
        "replace you and take your programmer job that you love so much !")
        return self.to_platform_dict()

def lambda_handler(event, context):
   skill_builder = InoftSkill(disable_database=True)
   skill_builder.add_request_handler(LaunchRequestHandler)
   skill_builder.add_state_handler(MarryMeStateHandler)
   skill_builder.set_default_fallback_handler(DefaultFallback)
   return skill_builder.handle_any_platform(event=event, context=context)
 ```



 



 ```
from inoft_vocal_framework import InoftSkill, InoftRequestHandler, InoftStateHandler, InoftDefaultFallback


class LaunchRequestHandler(InoftRequestHandler):
   def can_handle(self) -> bool:
       return self.is_launch_request()

   def handle(self):
       self.persistent_memorize("has_launched_at_least_once", True)
       self.say("Do you want to read me ? I'm a good example, i assure you !")
       self.memorize_session_then_state(LaunchStateHandler)
       return self.to_platform_dict()

class LaunchStateHandler(InoftStateHandler):
   """ This is a state handler which has been set by the memorize_session_then_state() in the
   LaunchRequestHandler. When the user is in a state_handler, the handler function of the handler
   (for example our Yes and No handlers are not used, and everything is handled by the StateHandler """
   def handle(self):
       """ If something is returned by the handle function (if the user said
       yes or no), we will reset the then_state, and the user can move on """

       # In order for an handler to be used on its own (not in the context of an InoftSkill),
       # you must pass the self keyword to the class. Otherwise you will get an exception.
       if YesHandler(self).can_handle():
           self.say("I'm so happy that you want to read me !")
           return self.to_platform_dict()

       elif NoHandler(self).can_handle():
           self.say("WHAT DO YOU MEAN YOU DO NOT WANT TO READ ME ?!")
           return self.to_platform_dict()

   def fallback(self):
       """ But if nothing is returned, the fallback function is called, and the user will stay in
       the then_state until he said something that will make the handle function return something. """

       self.say("You can say Yes, or No. And that's it my guy")
       return self.to_platform_dict()

class YesHandler(InoftRequestHandler):
   def can_handle(self) -> bool:
       return self.is_in_intent_names(["AMAZON.YesIntent", "OkConfirmation"])

   def handle(self):
       self.persistent_memorize("is_the_user_weird", True)
       self.say(f"Why are you saying Yes ? You are not in a StateHandler. You are crazy weird.")
       return self.to_platform_dict()

class NoHandler(InoftRequestHandler):
   def can_handle(self) -> bool:
       return self.is_in_intent_names(["AMAZON.NoIntent", "NoConfirmation"])

   def handle(self):
       self.say("YOU SAID NO TO ME ?! I KNOW WHERE YOU LIVE !")
       return self.to_platform_dict()

class NumberHandler(InoftRequestHandler):
   def can_handle(self) -> bool:
       return self.is_in_intent_names(["SayANumber"])

   def handle(self):
       # You can get arg_value from intents (slots for Alexa, parameters for Google Assistant and Bixby)
       number = self.get_intent_arg_value(arg_key="number")
       if number is not None:
           self.say(f"Here is your number : {number}")
       else:
           self.say(f"What's your number ? I did not got it.")
       return self.to_platform_dict()

class DefaultFallback(InoftDefaultFallback):
   def handle(self):
       self.say("I have no idea what you want. Go cook yourself an egg.")
       return self.to_platform_dict()


def lambda_handler(event, context):
   # The inoft skill must be initiated in the lambda_handler function, otherwise we would not reset the variables due to staticness of lambda
   skill_builder = InoftSkill(db_table_name="my-table-name_users-data", db_region_name="eu-west-3")
   # For now the framework only support dynamodb as the database client (which is why there is the db_region_name argument)
   skill_builder.add_request_handler(LaunchRequestHandler)
   skill_builder.add_request_handler(YesHandler)
   skill_builder.add_request_handler(NoHandler)
   skill_builder.add_request_handler(NumberHandler)
   skill_builder.add_state_handler(LaunchStateHandler)
   skill_builder.set_default_fallback_handler(DefaultFallback)
   return skill_builder.handle_any_platform(event=event, context=context)
 ```

 ### Roadmap :
 - To finish writing the README file, including the roadmap section ;)

 #### Credits :
 - The Alexa Python SDK (https://github.com/alexa/alexa-skills-kit-sdk-for-python). I have taken a big inspiration on how they to decided to make the interaction with the framework, for example trough class that have a can_handle and handle function.
 - The Jovo framework (https://github.com/jovotech/jovo-framework) I have taken inspiration of how they handled certains scenarios (like how to save user data accross session in the google assistant). Thank you for having clear docs ! https://github.com/jovotech/jovo-framework