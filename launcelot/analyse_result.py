from BeautifulSoup import BeautifulSoup
result_file_name = 'pystdlib_server_result.xml'
with open(result_file_name) as bench:
    soup = BeautifulSoup(bench.read())
    analyse_result_file = result_file_name.split('.')[0] + '.txt'
    with open(analyse_result_file, 'w') as result_file:
        write_to_result = lambda s: result_file.write(s)
        conn_count_ps = []
        for cycle in range(12):
            conn_count = 0
            average = 0.0
            for result in soup('testresult', {'cycle':'%03d' % cycle}):
                conn_count += 1
                average += float(result['duration'])
                if conn_count == 1:
                    starttime = float(result['time'])
                else:
                    endtime = float(result['time'])
            duration = endtime - starttime
            write_to_result('cycle: %02d | ' % (cycle))
            write_to_result('average: %fs | ' % (average / conn_count))
            write_to_result('duration: %.2fs | ' % (duration))
            write_to_result('conn_count: %d | ' % (conn_count))
            write_to_result('conn_count_ps: %d' % (conn_count / duration))
            write_to_result('\n')
            conn_count_ps.append(int(conn_count / duration))
        write_to_result('to run those in matlab...\n')
        for config in soup('config', {'key': 'cycles'}):
            write_to_result('client_count = %s;\n' % config['value'])
        write_to_result('conn_count_ps = %r;\n' % conn_count_ps)
        write_to_result('plot(client_count, conn_count_ps);\n')