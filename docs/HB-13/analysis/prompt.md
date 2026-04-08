Create an analysis and formulate requirements. The task is to add a client entity into the #codebase . The client can have multiple accounts, while every account shall belong to a client. The client entity should have an ID, name and a national number, which must be unique. We need to define two data access points:

one which would list all the clients
one which would show details of one client
I need 3 markdown documents in which the relevant requirements will be placed, each for one role. The Definition of Done for those are:

Developers: the functionality is properly developed
Testers: the functionality is properly tested by automated tests
Operations: the migration script is available so that existing databases might be altered
Place those documents in docs/HB-13/analysis folder.