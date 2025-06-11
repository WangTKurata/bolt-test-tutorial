# bolt-test-tutorial

Environment variables
~~~
$env:SLACK_BOT_TOKEN="xoxb-XXXXX"
$env:SLACK_APP_TOKEN="xapp-YYYYY"
~~~

.gitignore に .vscode/ を追加しておいて、.vscode/launch.json に書いておくと良い。

~~~
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-XXXXX",
        "SLACK_APP_TOKEN": "xapp-YYYYY"
      }
~~~