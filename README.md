
# about

Exposes a simple class based component to create a series of request based on a seed file

# dependencies

At the core we're using Python 3, and the libraries required for the script to work are:

* aiohttp - asynchronous http calls
* asyncio - event loop and async / await function support

If you have pip installed, you could install all dependencies by:

```
# install the dependencies

python3 -m pip install --user aiohttp
python3 -m pip install --user asyncio
python3 -m pip install --user matplotlib
```

# how to use it

If you just want to use it as a CLI, you have the following parameters available:

* `inputfile` - Indicates the file with all the URLs to hit
* `lfrom` - The start line number from the file (default to 0)
* `lto` - The the line number from the file (default to 9)
* `wait` - The time to wait in between the batches
* `size` - The requests to be sent per batch

## manually configuring a test

Make sure you have a seed file that contains all the HTTP (get) requests to be made to stress the server

Then use the class `HTTPLoadGenerator` to configure the test, for example:

```
# configure the test
# set the requests per second (rps) to 10
# set the time to wait in between batches to 10 seconds
test = HTTPLoadGenerator(seed_file='/full/path/to/your/file',
  spare_time=10,
  rps=10
)

# start the test
test.start()
```

If you want to save the requests into a file, you can just:

```
test.save_results_to_file(filename='test-1.output')
```

This will save the file with a CSV style with the following information:

* `START_TIME` - The time on which the request started (based on the event loop start time)
* `END_TIME` - The time on which the request finished (based on the event loop start time)
* `ELAPSED_TIME` - The time it took for this request to finish
* `SUCCESS_RESPONSE` - Indicates if the response was successful or not

