select * from tgommo_creature c;
select * from tgommo_environment_creature ec order by ec.environment_id;
select * from tgommo_user_creature tuc;

select * from users;
select * from user_avatar ua;
select * from tgommo_user_profile_avatar_link ual;
select * from tgommo_user_avatar_unlock_condition uauc;
select * from tgommo_user_avatar_nickname_link uanl;

select * from tgommo_inventory_item tii;
select * from tgommo_user_item_inventory_link tuiil;

SELECT * from tgommo_collection tc;
--------------------------------------------------------------------------------------------------------
ALTER TABLE tgommo_environment ADD COLUMN local_img_suffix TEXT DEFAULT '';
--------------------------------------------------------------------------------------------------------


---------------------------------------------------------------------------------------------------------
DROP TABLE tgommo_creature;
DROP TABLE tgommo_environment;
DROP TABLE tgommo_environment_creature;
DROP TABLE tgommo_user_creature;

DROP TABLE user_avatar;
DROP TABLE tgommo_user_profile_avatar_link;
DROP TABLE tgommo_user_avatar_unlock_condition;


