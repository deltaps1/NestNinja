# WIP-document

This document describes the features that needs to be implemented in NestNinja.
It also defines the vocabulary and concepts used to understand the module. 

# Why NestNinja?
Have you ever experienced the tediousness of dealing with cleaning and flattening deaply nested JSON structures?
NestNinja is a library made to ease the proces of cleaning and transforming deeply nested JSON structures to flat formats.
The philosophy of NestNinja is control and intention. 
However, NestNinja also follows an analysis based approach were you analyse your structure before setting up permanent cleaning pipelines. 
Also, NestNinja wants to be a framework were you reliable can create pipelines for dealing with JSON structures in a regular and automated fashion. 

# Concepts
This section describes the concepts of the NestNinja module. 

## List of dictionaries
The main object that Nestninja deals with is a list og dictionaries (list of dicts). 
In NestNinja a list of dictionaries is called a `LoD`.
Every aspect of NestNinja is focused on manipulating these objects.

In NestNinja a underlying key in one of the dictionaries in the list is called a subkey. 
The underlying value under the subkey is called a subvalue. 


## Navigation
One can use navigation to go from the LoD to a the values of a subkey.
This creates a new LoD object.

Therefore, only subvalues containing lists of dictionaries can be used when navigating. 


## Splits
Somtimes there are many different datatypes found under the subvalues in a LoD.
Here you want to split the data to  handle the types appropiately. 


## Explosions (Implemented)
Explosions mostly work like the Pandas function of the same name.
When you have a field containing lists then you can use the explode function. 

## Detachments
Detachments work by creating a link to the parent object so it's possible to create a relational database.

# Ideas

## Tree view
https://www.willmcgugan.com/blog/tech/post/rich-tree/

# ToDo
- [ ] Fix the error handler
- [ ] Conceptualise the splitting features
- [ ] Go through all the functions and make a plan for everything.
- [ ] Go through functions and test cases to see if anything is missing.
- [ ] Create a functionality list to  make sure that everythin is accounted for
- [ ] Create a SQL exporter function that can compare dtypes and write to an DB
    - Create a pd.io.sql.get_schema() like functionality



