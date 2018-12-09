# gmailcli

a simple hack of a CLI for gmail.  Currently only supports listing and downloading of raw emails, as well as attachments.  I created this quickly to download a bunch of attachments.  Use at your own risk.

## sample usage

```
python3 gmailcli.py -c secrets/credentials.json -t secrets/token.json -q "after:2018-12-08 has:attachments" -o savedir save_attachments >index.csv
```

You need to create the file `credentials.json` by following the first step of the instructions at the following page:
[https://developers.google.com/gmail/api/quickstart/python](https://developers.google.com/gmail/api/quickstart/python).

`token.json` will be created after an interactive challenge in the browser if it doesn't exist.

Beside "save_attachments" two other commands are available, namely, "save_raw" (to save .eml files), and "print_info".

The utility will also print out the message id and the following header fields: Date, From, To, and Subject, in CSV format.