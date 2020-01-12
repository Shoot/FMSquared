# fm²

A package that allows you to simply create collages from your Last FM listening history, such as the one below.
![Collage image](https://i.imgur.com/ddjiN3a.png)

## Getting Started
### Prerequisites
- Python 3
- A Last FM API account

You can find the latest version of Python 3 at [this link](https://www.python.org/downloads/), download the correct version for your system and install it.
In order to get a Last FM API account you need to go to [this link](https://www.last.fm/api/account/create) and follow the instructions. Once you've done that, make a note of your API key, as you'll need it to use the program.

### Installing
```
pip install git+git://github.com/Shoot/FMSquared.git
```
Or, clone the latest version to a folder and install it using `setup.py`, like below.
```
py setup.py install
```

### Usage
```
fmsquared <token> <user> -width <width> -height <height> -period <time period to use>
```
More information on each of these is available by using the help command below.
```
fmsquared --help
```

### License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/Shoot/FMSquared/LICENSE) file for details.