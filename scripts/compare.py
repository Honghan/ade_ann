import os,json
import argparse

def get_file(file_list_lstm, slam_dir):
    with open(file_list_lstm) as f:
        for out in [line.rstrip() for line in f][:-1]:
            print(out)
            docId = out.split('-')[-1]
            slam_file = os.path.join(slam_dir,docId)
            data = []
            with open(out) as lstmf:
                for line in lstmf:
                    data.append(json.loads(line))
            with open(slam_file.strip('\n')) as slamf:
               slam_result = slamf.read()
            percent,missing_ade = compare_result(data,slam_result)
            return docId, percent, missing_ade

def compare_result(lstm,slam):

    missing_ade = []
    a = slam.split(",")
    end = len(a) - 2
    count = 0
    for i in range(2,end,5):
      to_find = a[i][2:-1]
      find = 0
      count+=1
      try:
          for x in lstm[0]:
                 for d in x.values():
                     if(to_find == str(d)):
                        find = 1
          if(find == 0):
              missing_ade.append(to_find)
      except ValueError as e:
                 pass
    found = count - len(missing_ade)
    percent_found = str(float(found)/count * 100) + "%"

    return percent_found, str(missing_ade)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input',dest='inputlist',type= str,help ='location of input files')
    parser.add_argument('-s', '--slam', dest='slamdir', type=str, help='location of slam dir.')
    parser.add_argument('-o','--output',dest='output',type= str,help ='location of output file.')
    parser.add_argument('-e','--extension',dest='extension',type= str,default=None,help ='Extension of the files e.g. \'.txt\'.If you want files with no extensions use -1')

    args= parser.parse_args()
    if not (args.inputlist and args.output):
        parser.error('both input dir and output file are required params')
    with open(args.output,'w') as fout:
        result=get_file(args.inputlist,args.slamdir)
        fout.write(','.join(result))
