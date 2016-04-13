use myblog;
create table myevents (
  `event_id` varchar(50) not null,
  `start_time` real not null,
  `end_time` real not null,
  `pause_inter` real not null,
  `inter_time` real not null,
  `time_zone` real not null,
  `event_title` varchar(100) not null,
  `event_type` smallint not null,
  `event_ctt` text not null,
  key `idx_created_at` (`start_timemyevents`),
  primary key(`event_id`)
) engine=innodb default charset=utf8;