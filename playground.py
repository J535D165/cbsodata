import pandas

import cbsodata

# cbsodata.get_data('82010NED', dir='testdownload')
# 

for k, v in cbsodata.get_info('82010NED').iteritems():
    print (k )
    # print v
   

# print cbsodata.get_meta('82010NED', 'DataProperties')

# print pandas.DataFrame(cbsodata.get_table_list())