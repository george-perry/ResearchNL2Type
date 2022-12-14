import os
import subprocess
import json
import threading
from glob import glob
import ast
from ast2json import ast2json

#/home/rabee/thesis/master_thesis_rabee_sohail/data_extraction/data/js_temp
missed = 0
threadLock = threading.Lock()
output_file_index = 0
num_funcs = 0
num_files = 0


def invoke(config):
    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(config['input_dir']) for f in filenames]
    # with open(config['input_file']) as files_list:
    #     files = files_list.read().splitlines()


    funcs = []
    print "number of files is: ", len(files)
    # print files
    jsCommand = "jsdoc -X "
    num_funcs = 0
    missed = 0
    count = 0
    for index, file in enumerate(files):
        print "\nNEW FILE \n"
        try:
            if file[-2:] == "js":
                output = subprocess.check_output(jsCommand + file, shell=True)
                # print output

                # print output
            elif file[-2:] == "py":

                print "\nPYTHON\n"

                with open(file, "r") as py_file:
                    py_code = py_file.read()  # reads the file in its entirety
                    parsed_code = ast.parse(py_code)

                    toJSON = ast2json(parsed_code)['body']

                    comment = toJSON[0]['body'][0]['value']['s']
                    toJSON.append({'comment': comment})

                    print toJSON, "\n\n"
                    output = json.dumps(toJSON)
                    print output

            funcs_json = to_valid_json(output)

            print(funcs_json)

            if index % 10 == 0:
                print "Processed files {}".format(index)
            for index, func_json in enumerate(funcs_json):
                # if "kind" in func_json and func_json["kind"] == "function":
                funcs.append(func_json)

            if len(funcs) > 10000:
                count += 1
                write_funcs_to_file(funcs, count, config['output_dir'])
                num_funcs += len(funcs)
                funcs = []
        except subprocess.CalledProcessError ,e:
            print e
            missed += 1

    count += 1
    write_funcs_to_file(funcs, count, config['output_dir'])
    num_funcs += len(funcs)

    print "the number of files missed is: {}, the total number of functions processed is: {}".format(missed, num_funcs)

def to_valid_json(jsonString):
    try:
        return json.loads(jsonString)
    except ValueError:
        print("\n\n\n")
        return ""

def write_funcs_to_file(funcs, index, output_dir):
    out_file_name = "jsdoc" + "_"+ str(index)

    print "\n\n\n", funcs, out_file_name

    with open(os.path.join(output_dir, out_file_name + ".json"),
              'w') as out_file:
        json.dump(funcs, out_file)
