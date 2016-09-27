from db.models import Event


def parse_event(line):
    line_list = line.split(";")

    res_dict = {"event_id": line_list[0].strip('"'),
                "start_time": float(line_list[1]),
                "end_time": float(line_list[2]),
                "pause_inter": float(line_list[3]),
                "inter_time": float(line_list[4]),
                "time_zone": float(line_list[5]),
                "event_title": line_list[6].strip('"'),
                "event_type": int(line_list[7]),
                "event_ctt": (";".join(line_list[8:])).strip('"\n ')}
    return res_dict


def backup_from_file(file_name):
    with open(file_name) as f:
        f.readline()
        for line in f:
            event_dict = parse_event(line)
            this_event = Event(**event_dict)
            this_event.insert()

if __name__ == "__main__":
    file_name = './backup/backup_20160621.csv'
    with open('./backup/test.csv') as f:
        for line in f:
            event_dict = parse_event(line)
            print event_dict