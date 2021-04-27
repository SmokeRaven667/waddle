# waddle
the penguins api and tooling around aws's parameter store
![codebuild](https://codebuild.us-east-2.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiUU82MEFwb2JTUzJ2OFJSOUI4eURSc01BNnBNb04zVTRvaUZxTERxb3U3Ui9HdkVJRUllOHBUdlNXVGpGVXpUeXllVkVncVE4cDIxcFBIMzh6SFFMUWFzPSIsIml2UGFyYW1ldGVyU3BlYyI6IkJlcmc3clNIbVVBaFRCWFUiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)

## ParamBunch

Lets you access secrets stored in a file or from parameter store!

### From a file

Create a file called test.yml that will hold your config.  
It can include both secrets and non-secrets

```yaml
meta:
  kms_key: dev
  region: us-west-2
  profile: mycompany
aws.username: aws-user
```

Now add a secret to that file using the waddle cli

```bash
waddle add-secret -f /path/to/test.yml aws.password
```

waddle will prompt you to enter in the secret.  As long as you have a 
kms key called dev, waddle will add a kms-data-key-encrypted secret into 
`test.yml`.  

Now you can access configuration values in the test.yml configuration file
using the following syntax:

```python
from waddle import ParamBunch
conf = ParamBunch(filename='/path/to/test.yml')
AWS_USERNAME = conf.aws.username
AWS_PASSWORD = conf.get('aws.password', 'some default value')
```  

### But I want to use parameter store </whine>

You can also load configs straight from AWS parameter store by providing a 
prefix.

```python
from waddle import ParamBunch
conf = ParamBunch(prefix='/path/to/parameters')
# Access /path/to/paramaters/aws/username
AWS_USERNAME = conf.aws.username
```  

## want to waddle your secrets up to SSM from a file?

In certain cases, you may want to keep files locally, but then push them
to aws as part of CI/CD.  For example, if you want to keep a centralized 
repository of your secrets that is shared among developers, you can encrypt
secrets in your config files using waddle.  For application deployment, you can
push those files up to ssm using `waddle deploy` and/or delete them from ssm
using `waddle undeploy`.

```bash
waddle deploy -f /path/to/params.yml
```

- or -

```bash
waddle undeploy -f /path/to/params.yml
```

## Bunch

A class that offers pathy semantics 
to access values in a dictionary.

### Bunch -- general usage
e.g.,

```python
from waddle import Bunch
values = {
    'a': {
        'b': {
            'c': True,
            'd': False,
        },        
    },
}
a = Bunch(values)
assert a.b.c == True
assert a.b.d == False
a.cat.name = 'mycat'
assert a['cat.name'] == 'mycat'
assert 'cat.age' in a == False
assert a.get('cat.age', 22) == 22
assert a.setdefault('cat.age', 45) == 45
``` 

### Bunch -- env

You can use the built-in `env` function to use
the dictionary as a set of default values that
can be overridden by environment variables.

e.g.,

```python
import os
from waddle import Bunch
os.environ['FTP_PASSWORD'] = 'password'
config = {
    'ftp': {
        'host': '127.0.0.1',
        'user': 'user',
    }
}
config = Bunch(config)
env = config.env()
assert env('FTP_PASSWORD') == 'password'
assert env('FTP_HOST') == '127.0.0.1'
```
