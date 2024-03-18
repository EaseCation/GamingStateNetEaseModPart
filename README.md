# 《我的世界中国版》GamingState 零件

利用状态机，来更加清晰地编写游戏流程。

---

使用状态机来编写游戏逻辑之所以更加清晰，主要是因为状态机能够帮助开发者以结构化的方式管理游戏的各种状态及其之间的转换。

状态机的核心思想是将游戏的运行分解为一系列的状态（比如等待、开始、进行中、结束等），每个状态都有明确的定义，以及在不同状态之间转换的规则。

这样做的好处包括但不限于： 

1. 清晰性和可预测性：每个状态都有明确的行为和转换条件，这使得游戏的行为和流程变得非常清晰和可预测。 

2. 易于维护和扩展：当游戏需要添加新的特性或修改现有逻辑时，开发者可以更容易地理解和修改状态机，而不是深入到复杂的、交织在一起的代码逻辑中。 

3. 错误减少：由于游戏逻辑被明确地分割到各个状态中，减少了不同逻辑部分之间的相互干扰，从而减少了错误的发生。以Minecraft的小游戏开发为例，我们可以考虑“BedWars（起床战争）”游戏。在这个游戏中，可以设定几个主要状态：等待玩家加入、游戏准备、游戏进行中、游戏结束。每个状态代表游戏流程的一个阶段： 

  - 等待玩家加入：这个状态负责等待足够的玩家加入游戏。状态机在这个状态下会监控玩家的加入，并在达到预定数量时转换到游戏准备状态。 
  - 游戏准备：在这个状态，游戏会为所有玩家分配队伍，生成资源，设置游戏环境等准备工作。完成所有准备工作后，状态机将游戏推进到游戏进行中状态。 
  - 游戏进行中：这是游戏的主要阶段，玩家在这里争夺胜利。这个状态会持续直到达成游戏结束的条件（比如某个队伍胜利），然后转换到游戏结束状态。 
  - 游戏结束：在这个状态，游戏会显示胜利的队伍，处理排名和奖励分发。之后，可能会将玩家重定向回大厅，或是准备下一轮游戏。

使用状态机，每个阶段的逻辑都被清晰地隔离开来，开发者能够更容易地管理和维护游戏逻辑，同时也为玩家提供了流畅和一致的游戏体验。

> 本框架在EC的Nukkit插件中使用，以此开发了起床战争、密室杀手、空岛战争、超级战墙、圣符传说等各种题材的游戏，用了之后都说好，代码相比于远古屎山那是清晰太多了啊～

---

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