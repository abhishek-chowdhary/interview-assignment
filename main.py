from service.ecs.cluster.cluster_details import final_result

def main():
    print('Started the program............')

    final_result(path = './account_config.json')

    print('Finished the program...........')

if __name__ == '__main__':
    main()