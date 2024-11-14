# logBook
Simple and it just works software to help generate metadata in for satellite passages

The aim is to make something that uncomplicated, simple to use, requires no dependencies and it just works

Usefull for tracking satelites, logging passes and generating metadata for the passes. But in the future the goal is to be able to support more than just satelites. It could be adaptable to a point that just by changing the configuration file you could use it for other purposes

## GQRX
There are two main features that are needed for this project and are missing from GQRX. The first one is the ability to start and stop recording the iq data remotely. The second one is the ability to have more than one socket connected.

The reason why we need two sockets, is because one is used by gpredict to correct doppler and the oder would be used by this program to get the desired data.

For these two reasons a custom fork of gqrx has been created with the required features to work with this project. The fork can be found in my repository.

The fork is currently missing the implementation of the second socket. An alternative to this would be for this program receive the commands from gpredict and forward them to gqrx.

## Features
- [x] Notes the angle and azimuth the signal was received at
    - Using rotctl to communicate with the rotor 
- [x] Notes the time the signal was received
- [ ] Note the frequency of the signal
    - With gqrx
- [ ] Note the signal strength
    - With gqrx
- [ ] Start and stop iq recording via the ui
    - With gqrx
- [ ] Record gain settings
    - With gqrx

It has a simple ui that allows the user to mark when specific events happen




## Todo
- [ ] Add images of the ui
- [ ] Better explanantion and why
- [ ] Add a section on how to use it

- [ ] Countdown counters should go to negative
- [ ] Cut raw file automatically after stop recording
- [ ] Configuration file for the hostnames and ips
- [ ] Configuration file for the countdowns
- [ ] Configuration file for the ui 
- [ ] Dump metadata if application is closed
- [ ] Add a way to add notes to the metadata
- [ ] make a super class that gqrx and rotctl inherit from
- [ ] Long beacong should be a beacon as well
- [ ] Solve gqrx communication
- [ ] Make launcher to launch everything at once
- [ ] Add logging