# Efficiency Booster

This is a simple program to boost your efficiency by keep track what you're doing.

# Requirement
0. Python 2.7
1. MySQL
2. mysql-connector-python: `pip install mysql-connector-python --allow-external mysql-connector-python`

# Usage
0. Create the database and tables for events by `schema.sql`
1. Set the `config.py` file, fill in the database access information.
2. Open Terminal and run `$python app.py`:
    - `db`: Database access information.
    - `types`: The name of types of events you want to create.
    - `scores`: The scores you would get for each event type. 
3. Press `CTRL`+`C` to interrupt the program and enter command mode, the supported command are listed below:
    - `s` or `start`: Create a new event.
    - `p` or `pause`: Pause current event.
    - `r` or `resume`: Resume a certain paused event.
    - `e` or `end`: End current event.
    - `lsd` (list day): Show the events you've done for last 24 hours.
    - `lsw` (list week): Show the events you've done for last 7 days.
    - `lsm` (list month): Show the events you've done for last 30 days.
    - `q` or `quit`: Exit command mode.
    - `exit`: Exit the program

## Life is short, I use Python!  : )