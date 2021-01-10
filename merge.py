import os
import json
import math
import time


index_path = 'index'
files = sorted(os.listdir(index_path))
N = len(files) #files in dir


def merge_vals(old_dict, new_dict):
    for key in new_dict:
        if key in old_dict.keys():
            old_dict[key] = sorted(old_dict[key].extend(new_dict[key]))
        else:
            old_dict[key] = new_dict[key]
    
    return old_dict

#write the files as file_index.txt
#steps for iterative merge
file_index = 0
while N != 1:
    print('\nN = ', N)
    batch_factor = int(math.log(N, 2)) + 1
    batch_factor = min(batch_factor, N)
    while file_index < N:
        batch_files = files[file_index : file_index + batch_factor]
        postings = {}

        #subiterations for merging a batch
        #write postings for reach batch
        for i in range(batch_factor):
            filename = os.path.join(index_path, batch_files[i])
            print('reading ', filename)
            with open(filename) as f:
                # print('file: ', [l for l in f])
                for line in f:
                    new_posting = json.loads(line)
                    for key, val in new_posting.items():
                        if key in postings.keys():
                            new_val = merge_vals(postings[key], val)
                            postings[key] = dict(sorted(new_val.items(), key=lambda t: t[0]))
                        else:
                            postings[key] = val
            postings = dict(sorted(postings.items(), key=lambda t: t[0]))

        for rm in batch_files:
            filename = os.pat.join(index_path, rm)
            os.remove(filename) 
            print('removed ', rm)
            print('-------------')
        #
        #
        #wirte batch index to folder
        new_file = open(os.path.join(index_path, '{}.txt'.format(file_index)), 'w')
        new_file.write(json.dumps(postings))
        new_file.close()
        print('created ', new_file, ' with postings\n')
        #
        #updating file_index after writing file_index.txt
        file_index += batch_factor
        N -= batch_factor
    
    #update files list
    files = sorted(os.listdir(index_path))
    N = len(files)
    file_index = 0
    time.sleep(1)