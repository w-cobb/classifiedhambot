create table users (
    id          serial primary key,
    username    varchar not null
);

create table trackers (
    id          serial primary key,
    username    varchar not null,
    item_name   text not null,
    created_at  timestamptz default now()
);

create index on trackers (username);

create table listings (
    id          serial primary key,
    item_name   text not null,
    item_url    text not null,
    created_at  timestamptz default now()
);

create table alerts (
    id          serial primary key,
    tracker_id  int not null,
    listing_id  int not null,
    username    varchar not null,
    triggered   boolean default false,
    created_at timestamptz default now()
);