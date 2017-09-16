import json
import re
import threading
import Queue
import time

## RegEx Proto: "o1134453081","(.*?)"

class Bookkeeper(threading.Thread):
    book = ''
    record = []

    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = Queue.Queue()

    def run(self):
        while(True):
            data = self.queue.get(True)
            self.record.append(data['data'])
            if data['mode'] == 'set':
                self.book = data['data']
            elif data['mode'] == 'append':
                new_data_object = json.loads(data['data'])
                for data in new_data_object['us'][0]['d']:
                    sub_text = '"' + str(data[0]) + '","' + str(data[1]) + '"'
                    self.book = re.sub('"' + data[0] +'","(.*?)"', sub_text, self.book)
            
            log_file = open("log/query_log_" + time.strftime('%Y-%m-%d %H-%M-%S') + ".json", 'w')
            encoded = data['data'].text.encode('utf8')
            log_file.write(encoded)
            log_file.close()            
        

    def set(self, mode, data_str):
        data = {
            'mode': mode,
            'data': data_str
        }
        self.queue.put_nowait(data)

