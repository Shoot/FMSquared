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
fmsquared <token> <user>
```
This is the base command you will have to use any time you run the program. Additional options are available below.

| Option | Required | Default | Help |
|--------|----------|---------|------|
| token | ✓ | None | Your Last.fm API token |
| user | ✓ | None | The username of the Last.fm profile to create the collage from |
| -width | ✗ | 3 | The amount of albums to display horizontally |
| -height | ✗ | 3 | The amount of albums to display vertically |
| -period | ✗ | overall | The time period to fetch data from |
| --no-empty | ✗ | False | Display only albums with album art |
| --artists-only | ✗ | False | Display only artist names in the text |
| --listen-count | ✗ | False | Display the amount of times the album has been listened to in the text |
| --verbose | ✗ | False | Increase the verbosity of outputs, including 'DEBUG' logging |

You can also see these commands and more information on them by typing the following command.
```
fmsquared --help
```
After running the first command successfully, a file called `final.png` will be saved to the directory you ran the program from.

### License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/Shoot/FMSquared/LICENSE) file for details.