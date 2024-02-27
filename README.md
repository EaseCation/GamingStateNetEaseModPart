# 《我的世界中国版》GamingState 零件

利用状态机，来更加清晰地编写游戏流程

## 状态机架构

- 这个状态机框架，设计为了可嵌套的树形结构。
  - 可在实例化或init时添加子状态 `add_sub_state(name: str, state_supplier: callable -> GamingState)`
    - Q: 为何这边接收的是state_supplier而不是实例化的state？
    - A: 每次新实例化可以避免在重新被调用时，老旧数据的污染问题，也就不需要手动清空数据。_如果就是需要保留数据，可以先在外部实例化后再通过lambda传入_
  - 通过在状态逻辑中调用 `next_sub_state`，来切换到下一状态。当没有下一状态时，会尝试切换父级的下一状态
  - 也可以调用 `toggle_sub_state` 来切换到指定的子状态

- 支持在具体状态中附加生命周期的逻辑: `with_init`, `with_enter`, `with_exit`, `with_tick`

- 支持在具体状态中编写仅在状态生效时的事件监听器: `listen_event`, `listen_engine_event`, `listen_preset_event`

基于这个框架，可以举一个小游戏的玩法例子：

**空岛战争 状态机**

- 等待游戏开始（所有玩家到位）
- 开局倒计时（10秒）
- 游戏初始化（这些是瞬间的状态，可复用的执行一些逻辑）
  - 传送玩家
  - 初始化箱子内容
- 游戏正式开始（本状态全局倒计时30分钟）
  - 子状态
    - 玩家定在空中倒计时（5秒）
    - 玩家下落到自己岛屿，并且由保护屏障禁止前往家外部
    - 保护屏障解除，正常PvP
    - 所有箱子刷新
    - 箱子再次刷新
    - 等待游戏结束
  - 监听器
    - 玩家死亡事件：判断游戏结束逻辑
  - 当状态超时时：游戏强制结束逻辑

## 如何使用？

本零件不能单独使用，需要编写新的零件，继承于本零件。然后在编写的新零件中，进行游戏逻辑的工作，并使用 `root_state` 进行状态管理。

详细步骤：

1. 导入本零件 `GamingState` 到已有项目的零件文件夹中：`behavior_packs/behavior_packs_xxxxx/Parts`
2. 在 MCStudio 中进入已有项目的编辑模式
3. 切换到 `预设` 功能页面
4. 点击底部 `资源管理` 的 `新建` 按钮
5. 选择 `EmptyPart 空零件` 点击下一步
6. 选择继承的零件 `GamingStatePart(来自自定义零件)`
7. 根据功能需求命名这个新零件，点击创建
8. **开始进行详细的业务状态机编写（详见下方业务逻辑编写文档）**
9. 在 MCStudio 编辑器中，创建新的 `空预设`，在 `预设` 功能页面从资源管理双击打开这个创建的预设
10. 在下方资源管理中找到刚刚创建的 `零件`，拖拽到打开的 `预设` 中
11. 最后，切换到 `关卡` 功能页面，将这个预设拖拽到世界中

## 业务状态编写

在你的零件代码中，在 `InitServer` 方法中，将你的业务状态添加到根状态 `self.root_state` 中：

```python
def InitServer(self):
    """
    @description 服务端的零件对象初始化入口
    """
    GamingStatePart.InitServer(self)
    self.root_state.set_loop()  # 设置是否始终循环
    self.root_state.add_sub_state('s1', TestGamingState)  # 第一种方式，直接Class
    self.root_state.add_sub_state('s2', TestGamingStateElse, arg)  # 如果带有额外参数，需要加在后方
    self.root_state.add_sub_state('s3', lambda parent: TestGamingStateEmmm(parent))  # 使用lambda传入额外参数会有延迟绑定
    self.root_state.next_sub_state()  # 别忘了调用 next_sub_state() 来启动子状态
```

为了编写业务状态，你需要创建一个新的class，继承于 GamingState（注意需要传入parent）：

```python
from ..GamingState.state.GamingState import GamingState

class TestGamingState(GamingState):
    def __init__(self, parent):
        GamingState.__init__(self, parent)
```

在实例化方法中，添加额外的生命周期逻辑：

```python
class TestGamingState(GamingState):
    
    def __init__(self, parent):
        GamingState.__init__(self, parent)
        self.with_init(self.on_init)
        self.with_enter(self.on_enter)
        self.with_exit(self.on_exit)
        
    def on_init(self):
        # 在GamingState中，随时通过self.get_part()获取到零件对象
        self.get_part().LogDebug('TestGamingState init')
        
    def on_enter(self):
        self.get_part().LogDebug('TestGamingState enter')
        
    def on_exit(self):
        self.get_part().LogDebug('TestGamingState exit')
```

在实例化方法中，添加事件监听器：

> 状态中的事件监听器，意义在于，这些事件只有在当前状态生效时才会触发。这样可以避免一些复杂的面条代码来判断是否应该执行事件。  
  例如在父状态中监听玩家死亡，而在子状态中监听玩家与某个方块的交互。

```python
class TestGamingState(GamingState):
    
    def __init__(self, parent):
        GamingState.__init__(self, parent)
        ...
        self.listen_event('namespace', 'systemName', 'PlayerDieEvent', self.on_player_death)  # 自定义监听各种事件
        self.listen_engine_event('PlayerDieEvent', self.on_player_death)  # 引擎事件
        self.listen_preset_event('CustomPresetEvent', self.on_preset_custom)  # 来自预设系统的事件
        self.listen_self_event('VectoryEvent', self.on_vectory)  # 来自自己Part的事件
        
    def on_player_death(self, args):
        print('TestGamingState.PlayerDieEvent', str(args))

    ...
```

目前额外提供了几个预置的状态，可以通过继承来实现：

```python
# 带有计时并在计时结束后自动切换到下一状态

from ..GamingState.state.TimedGamingState import TimedGamingState

class TestGamingState(TimedGamingState):
    def __init__(self, parent):
        TimedGamingState.__init__(self, parent, 10)  # 实例化的参为数duration，单位秒，类型为float
        self.with_time_out(self.on_time_out)
        self.with_tick(self.on_tick)
    
    def on_time_out(self):
        self.get_part().LogDebug('TestGamingState time out')

    def on_tick(self):
        self.get_part().LogDebug("TestGamingState.tick " + str(self.get_runtime_state_name()) + " " + str(self.get_formatted_time_left()))
```