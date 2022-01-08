# 基于 selenium 滑动验证码解锁
> 如果滑动解锁缺口有白边应该就可以通过`unlock_engine\slide_to_unlock.py` 进行解锁
> 已经封装完成 调用 `unlock_engine\slide_to_unlock.py` 的 `slide_to_unlock` 函数接口即可
## 滑动解锁思路 

- 滑动解锁图片缺口有白边、通过适当的灰度处理、二值化缺口边界很明显、可以得到滑动长度
- 在滑动的过程中因为有反爬、要模拟人工操作、所以要设计运动轨迹

> 当前代码里有 jd 登录示例代码