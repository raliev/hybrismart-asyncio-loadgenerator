#!/usr/bin/python3

# asynchronous processes
import asyncio
import aiohttp
# misc
from types import SimpleNamespace
from time import time
from json import loads
from math import ceil
import os


DEFAULT_HEADERS = {
    'Content-type': 'application/json',
}

class RequestTrace:
  '''
  Simple class to hold the request overall trace.

  attributes:

  * start_time - Indicates the start time of the request from the event loop
  * end_time - The end time of the request from the event loop (no matter if it was an error or not)
  * elapsed_time - Indicates the time that took for the request to be finished
  * response_status - The response status from the response object, if not set, will default to -1
  * is_success - Read-only property to evaluate if the response_status, will return True if response_status is 200 or 201, False otherwise
  * request_id - The request id
  '''
  SUCCESS_STATUS = [200, 201]
  def __init__(self, start_time = 0, end_time = 0, elapsed_time = 0, response_status=-1, request_id=1):
    self.start_time = start_time
    self.end_time = end_time
    self.elapsed_time = elapsed_time
    self.response_status = 0
    self.request_id = request_id

  @property
  def is_success(self):
    return self.response_status in RequestTrace.SUCCESS_STATUS

  def __str__(self):
    return '{}|{}|{}'.format(self.start_time, self.end_time, self.elapsed_time)

class HTTPLoadGenerator:
  '''
  Orchestrates the hits being made to the backend system using aiohttp library
  '''

  def __init__(self, rps=1, verbose=False, seed_file='', spare_time=5, from_line=0, to_line=9):
    self.execution_trace = []
    self.requests_per_second = rps
    self.verbose = verbose
    self.seed_file = seed_file
    self.spare_time = spare_time
    self.from_line = from_line
    self.to_line = to_line
    # loop that will be used across all the execution
    self.loop = None

  def get_headers(self):
    return DEFAULT_HEADERS

  async def on_request_start(self, session, ctx, params):
    # just attach the start time from the actual loop
    request_start_time = session.loop.time()
    request_id = ctx.single_request_id
    trace_obj = RequestTrace(
      start_time = request_start_time,
      request_id = request_id
    )
    ctx.request_trace_obj = trace_obj

  async def on_request_end(self, session, ctx, params):
    request_end_time = session.loop.time()
    trace_obj = ctx.request_trace_obj
    elapsed_time = request_end_time - trace_obj.start_time
    # update the stats for the individual request
    trace_obj.end_time = request_end_time
    trace_obj.elapsed_time = elapsed_time
    trace_obj.response_status = params.response.status
    # keep the trace of this request from the pool
    self.execution_trace.append(trace_obj)
  
  async def on_request_exception(self, session, ctx, params):
    print('There was an error while making the call to the backend system')

  def get_trace_config(self, request_index):
    trace_config = aiohttp.TraceConfig()
    def namespace_handler(**kwargs):
      return SimpleNamespace(single_request_id=request_index, **kwargs)
    # propagate the request number to the context
    trace_config.trace_config_ctx = namespace_handler
    trace_config.on_request_end.append(self.on_request_end)
    trace_config.on_request_start.append(self.on_request_start)
    trace_config.on_request_exception.append(self.on_request_exception)
    return trace_config

  async def send_data(self, endpoint, request_index):
    trace_config = self.get_trace_config(request_index)
    async with aiohttp.ClientSession(trace_configs=[trace_config]) as session:
      async with session.get(endpoint, headers=self.get_headers(), ssl=True) as res:
        if (self.verbose):
          print('Request finished with status {}'.format(res.status))

  def get_list_requests(self):
    with open(self.seed_file, 'r') as f:
      lines = f.readlines()
      to_line = min(len(lines), (self.to_line + 1))
      # chop the lines if indicated
      return lines[self.from_line:to_line]
    return []

  def get_subset(self, current_page, requests):
    page_start = current_page * self.requests_per_second
    page_end = current_page * self.requests_per_second + self.requests_per_second
    if (current_page > 0):
      page_start = page_start + 1
    if (page_end > len(requests)):
      page_end = len(requests)
    if (page_start == page_end):
      page_start = page_start - 1
    print('start {}; end {}'.format(page_start, page_end))
    return requests[page_start:page_end]
  
  async def submit_set(self, payload_set, page_number):
    tasks = []
    index = 0
    if (self.verbose):
      print('Sending batch number {} with size {}'.format(page_number, len(payload_set)))
    # create a list with all the tasks (http requests)
    for url_seed in payload_set:
      task = self.loop.create_task(self.send_data(url_seed.strip(), index))
      tasks.append(task)
      index = index + 1
    # hold for the set of posted elements
    return self.loop.create_task(asyncio.wait(tasks))

  async def execute_with_loop(self):
    self.loop = asyncio.get_event_loop()
    requests = self.get_list_requests()
    pages = ceil(len(requests) / self.requests_per_second)
    for page_index in range(0, pages):
      sub_set = self.get_subset(page_index, requests)
      # wait for the task so that we can hit every RPS and then give some spare time
      await self.submit_set(sub_set, page_index)
      # wait some seconds before the next batch of calls is sent!
      await asyncio.sleep(self.spare_time)

  def start(self):
    print('Starting test...')
    asyncio.run(self.execute_with_loop())
    print('Test finished!')

  def _generate_filename(self):
    return 'test-run-{}'.format(int(time()))

  @property
  def sorted_trace(self):
    return sorted(self.execution_trace, key=lambda x: x.start_time, reverse=False)

  def save_csv(self, filename, lines):
    filename = '{}.csv'.format(filename)
    with open(filename, 'w+') as f:
      f.write('\n'.join(lines))
      print('::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::')
      print('output file with name: {}'.format(filename))
      print('::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::')

  def save_results_to_file(self, filename=''):
    filename = filename if filename != '' else self._generate_filename()
    end_lines = []
    start_lines = []
    for request in self.sorted_trace:
      start_line = 'REQSTART|{}|{}'.format(request.request_id, request.start_time)
      start_lines.append(start_line)
      end_line = 'REQEND|{}|{}|{}|{}'.format(request.start_time, request.request_id, request.elapsed_time, request.response_status)
      end_lines.append(end_line)
    # save the CSV file
    self.save_csv('{}-start'.format(filename), start_lines)
    self.save_csv('{}-end'.format(filename), end_lines)

