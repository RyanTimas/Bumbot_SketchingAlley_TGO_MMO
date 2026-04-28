select * from tgommo_creature c;
select * from tgommo_environment_creature ec;
select * from tgommo_user_creature tuc;

select * from tgommo_environment e;

select * from users;
select * from tgommo_user_profile tup;
select * from user_avatar ua;
select * from tgommo_user_profile_avatar_link ual;
select * from tgommo_user_avatar_unlock_condition uauc;
select * from tgommo_user_avatar_nickname_link uanl;

select * from tgommo_inventory_item tii;
select * from tgommo_user_item_inventory_link tuiil;

SELECT * from tgommo_collection tc;
--------------------------------------------------------------------------------------------------------
    SELECT
        ua.avatar_num, ua.avatar_id, 
        ua.avatar_name, ua.avatar_type, ua.series, ua.is_parent_entry,
        ua.img_root,
        auc.unlock_query, auc.unlock_threshold, auc.is_secret,
        ua.shop_price,
        ua.unlock_startdate, ua.unlock_enddate
    FROM user_avatar ua
    LEFT JOIN tgommo_user_avatar_unlock_condition auc
        ON auc.avatar_id = ua.avatar_id
    LEFT JOIN tgommo_user_profile_avatar_link upal
    	ON upal.avatar_id = ua.avatar_id
    LEFT JOIN tgommo_user_avatar_nickname_link uanl
        ON uanl.avatar_id = ua.avatar_id
    WHERE 
 date('now') BETWEEN ua.unlock_startdate AND ua.unlock_enddate  AND  NOT EXISTS (SELECT 1 FROM tgommo_user_profile_avatar_link upal WHERE upal.avatar_id = ua.avatar_id AND upal.user_id = ?)  GROUP BY uanl.avatar_id;


    SELECT
        ua.avatar_num, ua.avatar_id, 
        ua.avatar_name, ua.avatar_type, ua.series, ua.is_parent_entry,
        ua.img_root,
        auc.unlock_query, auc.unlock_threshold, auc.is_secret,
        ua.shop_price,
        ua.unlock_startdate, ua.unlock_enddate
    FROM user_avatar ua
    LEFT JOIN tgommo_user_avatar_unlock_condition auc
        ON auc.avatar_id = ua.avatar_id
    LEFT JOIN tgommo_user_profile_avatar_link upal
    	ON upal.avatar_id = ua.avatar_id
    LEFT JOIN tgommo_user_avatar_nickname_link uanl
        ON uanl.avatar_id = ua.avatar_id
    WHERE 
 date('now') BETWEEN ua.unlock_startdate AND ua.unlock_enddate  GROUP BY ua.avatar_id;


---------------------------------------------------------------------------------------------------------
DROP TABLE tgommo_creature;
DROP TABLE tgommo_environment;
DROP TABLE tgommo_environment_creature;
DROP TABLE tgommo_user_creature;

DROP TABLE user_avatar;
DROP TABLE tgommo_user_profile_avatar_link;
DROP TABLE tgommo_user_avatar_unlock_condition;


