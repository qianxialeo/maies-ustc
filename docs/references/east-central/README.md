# 东区与中区的室外美术参考

收录 1 张校方总图、12 份东区资料和 9 份中区资料。表中图号直接链接原图，适合对照建筑体量、外饰、坡地、视线和沿路植被。逐图尺寸、出处与 SHA-256 见[来源清单](sources.json)。

**先用 G01 看三校区的位置。** 校方提供的 8550 × 6955 校园图可以辨认东、中、西区的相邻关系以及各自的路网与地标。其成图日期和地理配准信息待核。东区与中区通过金寨路下穿通道相连；校报在 2015 年已记载通道和中区林荫大道交付使用。2025 年的学习园地资料适合补足较老底图上中区东端的建筑变化。[校方地图](https://www.ustc.edu.cn/info/1009/1036.htm) · [交付使用记录](https://zgkdb.ustc.edu.cn/ndetail/2703) · [学习园地建筑师项目稿](https://www.archiposition.com/items/20250807105845)

**东区从老北门、樱花大道、眼镜湖到一教串起。** 第一教学楼北侧的两片水面隔樱花大道相望，一鉴亭位于东湖。可用 E02、E03、E05、E06 校正这条轴线上的树冠、亭廊和红砖立面。E07 是有图注的历史草坡照，只有起伏的形态依据。E11 对应东区郭沫若广场附近的咖啡馆，设计方另给出了改造平面与剖面。E12 是学生数字作品，供展示版参考。[眼镜湖与一鉴亭](https://zgkdb.ustc.edu.cn/ndetail/9977) · [一教与校园历史风貌](https://zgkdb.ustc.edu.cn/ndetail/3705) · [东区 USTC1958 改造项目稿](https://www.archina.com/index.php?a=show&g=works&id=2438&m=index)

**中区先看通道上方的学习园地，再看生活区与运动区。** C01、C02 给出校园尺度和体育场馆屋顶；C05 至 C09 把同一建筑的外观、占地、两个方向的剖面串起来。设计方说明下穿通道上方地面较高，可据此核对起伏方向与体量遮挡。图中高差适用于该场地，全校米制高程仍待核。2018 年校方记载中区已有六栋学生公寓，2022 年艺术教学中心启用。用图时保留各自年代。[建筑师项目稿](https://www.archdaily.com/zh/1033307/zhong-guo-ke-xue-ji-zhu-da-xue-zhong-xiao-qu-xue-xi-yuan-di-he-mu-jian-zhu) · [学生公寓迁入记录](https://news.ustc.edu.cn/info/1055/52673.htm) · [艺术教学中心启用](https://news.ustc.edu.cn/info/1055/80371.htm)

## 从参考图定位到地图

复原位置使用[仓库主底图](../../../data/campus3.osm)。东区和中区边界的 OSM way 分别是 `262614785`、`298734692`。校方总图可辅助定位，建筑高度和坡度需结合照片或剖面单独核对。[OSM 数据说明](../../../data/README.md)

| 参考图 | 在 campus3.osm 中查找 | 在漫游中怎样核对 |
| --- | --- | --- |
| E02、E03、E06 老北门至一教 | 老北门建筑 way `1135310350`，第一教学楼 way `265575551` | 可跳到“第一教学楼”。E06 记录了 2011 年的红砖外观，可用来复核当前通用教学楼配色。 |
| E04、E05 眼镜湖与一鉴亭 | 西半湖 way `290098995`，东半湖 relation `11542038`，亭岛内环 way `840391562` | 从一教向北看两片水面；东湖的两段步桥（way `306372996`、`306372998`）与亭岛保持可走。 |
| E07 玉泉南路草坡 | 道路 way `265032057` | 按道路定位草坡附近，坡高仍需其他资料。 |
| E08–E11 广场、报告厅、东图、东区 1958 | 对应 way 依次为 `306496885`、`267646980`、`284161541`、`268207470` | 菜单可直接跳到“东区图书馆”。广场用于对照轴线，其余三处可对照建筑外观。 |
| C04 艺术教学中心 | 艺术教学中心 way `1135310333`，相邻的学生活动中心 way `1135310332` | 菜单落点名为“中区学生活动中心”。对照 C04 时应认准艺术教学中心的入口标识。 |
| C05–C09 学习园地 | 以 C07 总平面定位建筑，并用 C08、C09 的方向判读剖面 | 可从“金寨路地下通道”开始查看。游戏根据两校区边界的最近点示意连接线，精确位置仍以项目图纸核对。 |

## 取用原图

表中图号可直接打开公开原图。在仓库根目录运行下列命令，可以只取本次要校对的几张图。

```bash
python scripts/fetch_reference_images.py E04 E05 C07
```

省略图号会取全部 22 份。文件保存在 `tmp/reference-images-east-central/`，Git 已忽略该目录。已有文件会核对 SHA-256。若原站更新图片导致校验失败，请先比对新旧版本，再更新来源记录。

校方及建筑师公开发表的图像供团队比对。直接使用原图制作发行素材时，按相应来源核对授权。E12 是数字创作示例。

## 校园总图

| 图号与原图 | 复原时可核对 | 时间与来源 |
| --- | --- | --- |
| [G01 东西中校区位置与总平面](https://www.ustc.edu.cn/__local/E/38/BD/1E3C1FCB91DBB0B5F992FB4DADF_351A881F_124B9C0.jpg) | 对照校区位置、主路、主要楼群和水面；逐栋轮廓另作核对。 | 校方校园地图，成图日期未标。 [来源页](https://www.ustc.edu.cn/info/1009/1036.htm) |

## 东区

| 图号与原图 | 复原时可核对 | 时间与来源 |
| --- | --- | --- |
| [E01 金寨路校门](https://zsb.ustc.edu.cn/_upload/article/images/a0/67/df1e62c54ec58f102027fcf3a970/d9593843-804f-4350-873f-b1f157d058b0.jpg) | 石材门框、门楣和临街尺度。 | 招办相册，拍摄日未标。 [来源页](https://zsb.ustc.edu.cn/xysj/list.htm) |
| [E02 老北门](https://zsb.ustc.edu.cn/_upload/article/images/92/3c/75b5a60d4f65b53d0f103e7dcb87/197597a2-d4b2-4aaf-83ae-038c167df87e.jpg) | 门楣轮廓和题字，勿与金寨路校门混用。 | 招办相册，拍摄日未标。 [来源页](https://zsb.ustc.edu.cn/xysj/list.htm) |
| [E03 樱花大道](https://sz.ustc.edu.cn/upload/202202/23/202202231537477199.jpg) | 双侧树冠、人行轴线与季节颜色。 | 图集发布于 2022-02-23，拍摄日未标。 [来源页](https://sz.ustc.edu.cn/wdxz_show/61.html) |
| [E04 眼镜湖](https://sz.ustc.edu.cn/upload/202202/23/202202231536326627.jpg) | 湖岸植被、水面及周边树线。 | 图集发布于 2022-02-23，拍摄日未标。 [来源页](https://sz.ustc.edu.cn/wdxz_show/61.html) |
| [E05 一鉴亭与曲廊](https://zgkdb.ustc.edu.cn/uploadfile/2026/0417/20260417154607281240.jpg) | 对照东湖亭顶和转折回廊与岸的连接。 | 校报刊期 2026-04-05，拍摄日未标。 [来源页](https://zgkdb.ustc.edu.cn/ndetail/9977) |
| [E06 一教红墙](https://business.ustc.edu.cn/_upload/article/images/10/8a/6ad6e27742f3b65f5edeb0fccbb9/W020111024389390634303.jpg) | 砖墙、窗列、转角与常绿树遮挡。 | 2011 年 10 月校园报道，单张拍摄日未标。 [来源页](https://business.ustc.edu.cn/2011/1026/c28419a526436/page.htm) |
| [E07 玉泉南路草坡](https://business.ustc.edu.cn/_upload/article/images/10/8a/6ad6e27742f3b65f5edeb0fccbb9/W020111024389390590682.jpg) | 图注指认为玉泉南路西侧草坡；只支持当时有缓起伏。 | 2011 年 10 月校园报道，单张拍摄日未标。 [来源页](https://business.ustc.edu.cn/2011/1026/c28419a526436/page.htm) |
| [E08 郭沫若广场轴线](https://sz.ustc.edu.cn/upload/202202/23/202202231536318112.jpg) | 广场纵深、植被和水景的空间层次。 | 图集发布于 2022-02-23，拍摄日未标。 [来源页](https://sz.ustc.edu.cn/wdxz_show/61.html) |
| [E09 水上报告厅](https://sz.ustc.edu.cn/upload/202202/23/202202231536317080.jpg) | 低层水平体量、窗带和邻近乔木。 | 图集发布于 2022-02-23，拍摄日未标。 [来源页](https://sz.ustc.edu.cn/wdxz_show/61.html) |
| [E10 图书馆入口](https://sz.ustc.edu.cn/upload/202202/23/202202231536319267.jpg) | 入口凹入、柱列及相邻立面的材料对比。 | 图集发布于 2022-02-23，拍摄日未标。 [来源页](https://sz.ustc.edu.cn/wdxz_show/61.html) |
| [E11 东区1958外立面](https://zsb.ustc.edu.cn/_upload/article/images/af/ec/10b4e11e4f87959e1539bb3a0c45/11163d90-726c-4891-93e3-7d0751155dac.jpg) | 树下的低层建筑、面向庭院的开口；与西区湖畔同名地标区分。 | 招办相册，拍摄日未标。 [来源页](https://zsb.ustc.edu.cn/xysj/list.htm) |
| [E12 方块科大樱花大道](https://ef.ustc.edu.cn/__local/B/E6/82/BB2F68222279F7F22AB85B6EC92_B3FBB34A_F9EC.jpg) | 活动展示用像素化创作先例。实景复原以 E03、E06 等作依据。 | 2023 年夏季项目报道；制作日未标。 [来源页](https://ef.ustc.edu.cn/info/1061/1946.htm) |

## 中区

| 图号与原图 | 复原时可核对 | 时间与来源 |
| --- | --- | --- |
| [C01 中区全景](https://sz.ustc.edu.cn/upload/202202/23/202202231537491422.jpg) | 宿舍楼列、运动场地与主路的总体关系。 | 图集发布于 2022-02-23，拍摄日未标。 [来源页](https://sz.ustc.edu.cn/wdxz_show/61.html) |
| [C02 综合体育中心](https://zsb.ustc.edu.cn/_upload/article/images/f3/a4/fa6391324b459183a0c3beb6fdbe/09a99786-20ea-45fe-8d3f-4cb262d1d425.jpg) | 主馆屋顶、圆形体量及室外球场排列。 | 招办相册；相机记录 2022-06-16。 [来源页](https://zsb.ustc.edu.cn/xysj/list.htm) |
| [C03 北门永怀初心雕塑](https://lfo.ustc.edu.cn/__local/D/D5/7A/EC21BB144EF32106FF3AC197A0F_B3742B9C_3591E.jpg) | 雕塑组、题字和背景石面的尺度。 | 校方校庆回顾；相机记录 2022-04-20。 [来源页](https://lfo.ustc.edu.cn/info/1007/1939.htm) |
| [C04 艺术教学中心入口标识](https://lfo.ustc.edu.cn/__local/5/68/72/37495388484D91B98C9FC5F9BB5_F6E57652_139A0.jpg) | 入口外墙、转角雨棚和标识，图中只覆盖局部。 | 相机记录 2022-06-13，早于同年 9 月正式启用。 [来源页](https://lfo.ustc.edu.cn/info/1007/1939.htm) |
| [C05 学习园地临场外观](https://images.adsttc.com/media/images/68a3/a388/07ae/347b/b5b5/98ad/large_jpg/learning-center-at-the-central-campus-of-ustc-atelier-heimat_10.jpg?1755554806) | 上层曲面、首层退让以及绿地与体量关系。 | 项目页列建成年份 2025，图像 EXIF 标作 2023-10-16。拍摄期未独立证实。 [魏溦 摄 · 图页](https://www.archdaily.com/zh/1033307/zhong-guo-ke-xue-ji-zhu-da-xue-zhong-xiao-qu-xue-xi-yuan-di-he-mu-jian-zhu/68a3a38807ae347bb5b598ad-zhong-guo-ke-xue-ji-zhu-da-xue-zhong-xiao-qu-xue-xi-yuan-di-he-mu-jian-zhu-zhao-pian) |
| [C06 学习园地与下穿通道](https://images.adsttc.com/media/images/68a3/a3d8/65bf/e163/962e/3fd8/large_jpg/learning-center-at-the-central-campus-of-ustc-atelier-heimat_14.jpg?1755554827) | 从高处辨认建筑、上部地面及下穿通道的叠置。 | 项目页列建成年份 2025，图像 EXIF 标作 2023-10-16。拍摄期未独立证实。 [是然建筑摄影 摄 · 图页](https://www.archdaily.com/zh/1033307/zhong-guo-ke-xue-ji-zhu-da-xue-zhong-xiao-qu-xue-xi-yuan-di-he-mu-jian-zhu/68a3a3d865bfe163962e3fd8-zhong-guo-ke-xue-ji-zhu-da-xue-zhong-xiao-qu-xue-xi-yuan-di-he-mu-jian-zhu-zhao-pian) |
| [C07 学习园地总平面](https://images.adsttc.com/media/images/68a3/a3de/6d0f/9641/8575/82bd/large_jpg/00-site-plan-c-heimat-architects-1.jpg?1755554816) | 对齐建筑占地、周围道路与场地边界。 | 合木建筑工作室，2025 年项目发表。 [来源页](https://www.archdaily.com/zh/1033307/zhong-guo-ke-xue-ji-zhu-da-xue-zhong-xiao-qu-xue-xi-yuan-di-he-mu-jian-zhu) |
| [C08 学习园地南北剖面](https://images.adsttc.com/media/images/68a3/a3df/07ae/347b/b5b5/98b6/large_jpg/03-north-south-section-c-heimat-architects-4.jpg?1755555011) | 对照各层体量、地面与下穿通道的位置。 | 合木建筑工作室，2025 年项目发表。 [来源页](https://www.archdaily.com/zh/1033307/zhong-guo-ke-xue-ji-zhu-da-xue-zhong-xiao-qu-xue-xi-yuan-di-he-mu-jian-zhu) |
| [C09 学习园地东西场地剖面](https://images.adsttc.com/media/images/68a3/a3de/65bf/e163/962e/3fdc/large_jpg/04-east-west-site-section-c-heimat-architects-5.jpg?1755554804) | 核对跨越场地的地面变化；剖面只适用于图示范围。 | 合木建筑工作室，2025 年项目发表。 [来源页](https://www.archdaily.com/zh/1033307/zhong-guo-ke-xue-ji-zhu-da-xue-zhong-xiao-qu-xue-xi-yuan-di-he-mu-jian-zhu) |
