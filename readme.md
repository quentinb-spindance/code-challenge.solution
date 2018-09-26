Quentin's Code Challenge Solution
=================================

*Note: This is an evolving document currently. I want to make this an* ideal *solution to the code challenge, something that can be used as a basis for validating other challenges. Becuase of this, I want to go beyond just "getting the job done".*

Running the Code
----------------
This is coded in python3 and requires (aside from corelibs), the [AWS IoT Python SDK](https://github.com/aws/aws-iot-device-sdk-python).

Once you've installed the requirements, you can run the code from terminal, with several options for arguments:

    -d | --debug | -v | --verbose
This will run the code with verbose statements, useful for debugging.


    -w [d] | --window [d]

Sets window size (for averages) to *d*, if d > 0. Default size is 4.


    -i [d] | --interval [d]

Sets the report interval to *d*, if d > 0. Default interval is 2.

Note that if you have both python 2 and python 3 installed, you will need to invoke this code with: 
    
    python3 <command name>
    