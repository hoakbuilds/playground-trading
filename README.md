```
 ______  __       ______   __  __   ______   ______   ______   __  __   __   __   _____    
/\  == \/\ \     /\  __ \ /\ \_\ \ /\  ___\ /\  == \ /\  __ \ /\ \/\ \ /\ "-.\ \ /\  __-.  
\ \  _-/\ \ \____\ \  __ \\ \____ \\ \ \__ \\ \  __< \ \ \/\ \\ \ \_\ \\ \ \-.  \\ \ \/\ \ 
 \ \_\   \ \_____\\ \_\ \_\\/\_____\\ \_____\\ \_\ \_\\ \_____\\ \_____\\ \_\\"\_\\ \____-'
  \/_/    \/_____/ \/_/\/_/ \/_____/ \/_____/ \/_/ /_/ \/_____/ \/_____/ \/_/ \/_/ \/₀.₁.₀/ 
                                                                                           
```

# playground
[![Build Status](https://api.cirrus-ci.com/github/murlokito/playground.svg)](https://cirrus-ci.com/github/murlokito/playground)

An OpenSSL wizard (GUI), created in the context of IT Security subject, at Universidade da Beira Inteiror (UBI) . Open sourced for the greater good.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for various purposes.

### Prerequisites

In order to be able to install and run the application you will need the following programs in your machine, check below for installation procedures.

```
Docker > 18 (optional)
Python >= 3.6
pip >=  20.1.1
pipenv >= version 2020.6.2 (prefered)
ta-libc == 0.4.0 (required for python TA-Lib)
ta-lib == 0.4.17 (required)
```

### Dependencies

#### TA-Lib

##### Linux

Download [ta-lib-0.4.0](http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz) and:

```
$ tar -xzf ta-lib-0.4.0-src.tar.gz
$ cd ta-lib/
$ ./configure --prefix=/usr
$ make
$ sudo make install
```

If you build TA-Lib using `make -jX` it will fail but that's OK! Simply rerun `make -jX` followed by `sudo make install`.

### Installing

You can install and run the application in several ways.

#### Docker [SOON]

Go to the root folder of the repository and, considering you have `Docker` installed on your machine, execute the following commands: 

```
#The following command will build the app from an alpine image to keep it small
make build_app

#The next command will simply run the container
make start_backend
```

#### Just pipenv things

In the root of the repository just run:

```
$ pipenv install
```

Make sure you have `pipenv installed`, otherwise install it:

```
$ pip3 install pipenv
```


## Built With

* [Flask](http://flask.pocoo.org/) - The web framework used

## Contributors

* **Hugo Carvalho** - *Maintainer* - [murlokito](https://github.com/murlokito)

See also the list of [contributors](https://github.com/murlokito/playground/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details