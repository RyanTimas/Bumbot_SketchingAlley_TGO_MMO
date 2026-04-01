select * from tgommo_creature c;
select * from tgommo_environment_creature ec;
select * from tgommo_user_creature tuc;

select * from tgommo_environment e;

select * from users;
select * from tgommo_user_profile tup;
select * from user_avatar ua;
select * from tgommo_user_profile_avatar_link ual;
select * from tgommo_user_avatar_unlock_condition uauc;

select * from tgommo_inventory_item tii;
select * from tgommo_user_item_inventory_link tuiil;

SELECT * from tgommo_collection tc;
--------------------------------------------------------------------------------------------------------


ALTER TABLE user_avatar ADD COLUMN shop_price INTEGER NOT NULL DEFAULT 0;
ALTER TABLE tgommo_inventory_item ADD COLUMN shop_price INTEGER NOT NULL DEFAULT 0;
ALTER TABLE tgommo_user_item_inventory_link ADD COLUMN last_purchase_date TIMESTAMP DEFAULT (datetime('now', '-1 day'));

---------------------------------------------------------------------------------------------------------
DROP TABLE tgommo_creature;
DROP TABLE tgommo_environment;
DROP TABLE tgommo_environment_creature;
DROP TABLE tgommo_user_creature;

DROP TABLE user_avatar;
DROP TABLE tgommo_user_profile_avatar_link;
DROP TABLE tgommo_user_avatar_unlock_condition;


