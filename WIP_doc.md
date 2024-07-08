# WIP-document

This document describes the features that needs to be implemented in NestNinja.
It also defines the vocabulary and concepts used to understand the module. 


# Why NestNinja?
...


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
...

## Detachments
Detachments work by creating a link to the parent object so it's possible to create a relational database.

# Ideas

## Tree view
https://www.willmcgugan.com/blog/tech/post/rich-tree/

