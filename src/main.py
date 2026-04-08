import tkinter as tk
from enum import Enum
import time
from collections import deque

class Direction(Enum):
    UP = 1
    DOWN = -1
    IDLE = 0

class ElevatorState(Enum):
    IDLE = "Ожидание"
    MOVING = "Движение"
    DOOR_OPEN = "Двери открыты"
    DOOR_CLOSING = "Закрытие дверей"

class Elevator:
    def __init__(self, num_floors=10, start_floor=1):
        self.num_floors = num_floors
        self.current_floor = start_floor
        self.target_floor = None
        self.direction = Direction.IDLE
        self.state = ElevatorState.IDLE
        
        # Запросы: внешние (вызов с этажа) и внутренние (кнопки в лифте)
        self.external_requests = set()  # вызовы с этажей
        self.internal_requests = set()  # нажатия кнопок внутри
        
        # Для алгоритма SCAN
        self.requests_queue = deque()
        
        # Время операций
        self.door_open_time = 3
        self.door_timer = 0
        self.floor_travel_time = 1
        self.travel_timer = 0

    def add_external_request(self, floor, direction):
        """Вызов лифта с этажа"""
        if 1 <= floor <= self.num_floors:
            self.external_requests.add((floor, direction))
            print(f"Вызов с этажа {floor} в направлении {direction.name}")

    def add_internal_request(self, floor):
        """Нажатие кнопки внутри лифта"""
        if 1 <= floor <= self.num_floors:
            self.internal_requests.add(floor)
            print(f"Нажата кнопка этажа {floor} внутри лифта")

    def update_requests_queue(self):
        """Обновление очереди запросов по алгоритму SCAN"""
        # Очищаем текущую очередь
        self.requests_queue.clear()
        
        # Собираем все целевые этажи
        all_targets = set()
        
        # Внутренние запросы всегда обрабатываются
        all_targets.update(self.internal_requests)
        
        # Внешние запросы обрабатываются в зависимости от направления
        for floor, req_direction in self.external_requests:
            # Если лифт в движении, учитываем направление
            if self.direction != Direction.IDLE:
                if req_direction == self.direction:
                    all_targets.add(floor)
                elif req_direction != self.direction and self.state == ElevatorState.IDLE:
                    all_targets.add(floor)
            else:
                all_targets.add(floor)
        
        # Сортируем согласно направлению движения (SCAN)
        if self.direction == Direction.UP or self.direction == Direction.IDLE:
            # Движемся вверх до самого верхнего запроса
            up_targets = [f for f in all_targets if f >= self.current_floor]
            up_targets.sort()
            self.requests_queue.extend(up_targets)
            
            # Затем вниз
            down_targets = [f for f in all_targets if f < self.current_floor]
            down_targets.sort(reverse=True)
            self.requests_queue.extend(down_targets)
            
        elif self.direction == Direction.DOWN:
            # Движемся вниз до самого нижнего запроса
            down_targets = [f for f in all_targets if f <= self.current_floor]
            down_targets.sort(reverse=True)
            self.requests_queue.extend(down_targets)
            
            # Затем вверх
            up_targets = [f for f in all_targets if f > self.current_floor]
            up_targets.sort()
            self.requests_queue.extend(up_targets)

    def update(self, dt):
        """Обновление состояния лифта (вызывается каждый кадр)"""
        
        if self.state == ElevatorState.IDLE:
            # Проверяем наличие запросов
            self.update_requests_queue()
            if self.requests_queue:
                self.target_floor = self.requests_queue[0]
                self.direction = Direction.UP if self.target_floor > self.current_floor else Direction.DOWN
                self.state = ElevatorState.MOVING
                print(f"Начинаю движение к этажу {self.target_floor}")
        
        elif self.state == ElevatorState.MOVING:
            self.travel_timer += dt
            
            if self.travel_timer >= self.floor_travel_time:
                self.travel_timer = 0
                
                # Перемещаемся на один этаж
                if self.direction == Direction.UP:
                    self.current_floor += 1
                elif self.direction == Direction.DOWN:
                    self.current_floor -= 1
                
                # Проверяем, достигли ли целевого этажа
                if self.current_floor == self.target_floor:
                    self.state = ElevatorState.DOOR_OPEN
                    self.door_timer = 0
                    print(f"Прибыл на этаж {self.current_floor}, открываю двери")
                    
                    # Удаляем обработанные запросы
                    self.internal_requests.discard(self.current_floor)
                    self.external_requests = {(f, d) for f, d in self.external_requests 
                                             if not (f == self.current_floor)}
                
                # Проверяем промежуточные запросы (для внутренних кнопок)
                if self.current_floor in self.internal_requests:
                    print(f"Остановка на этаже {self.current_floor} по внутреннему вызову")
                    self.target_floor = self.current_floor
                    self.state = ElevatorState.DOOR_OPEN
                    self.door_timer = 0
                    self.internal_requests.discard(self.current_floor)
        
        elif self.state == ElevatorState.DOOR_OPEN:
            self.door_timer += dt
            
            if self.door_timer >= self.door_open_time:
                self.state = ElevatorState.DOOR_CLOSING
                print("Закрываю двери")
        
        elif self.state == ElevatorState.DOOR_CLOSING:
            # Обновляем очередь запросов и продолжаем движение
            self.update_requests_queue()
            
            if self.requests_queue:
                if self.requests_queue[0] != self.current_floor:
                    self.target_floor = self.requests_queue[0]
                    self.direction = Direction.UP if self.target_floor > self.current_floor else Direction.DOWN
                    self.state = ElevatorState.MOVING
                else:
                    # Если следующий запрос - текущий этаж, удаляем его
                    self.requests_queue.popleft()
                    self.state = ElevatorState.IDLE
            else:
                self.direction = Direction.IDLE
                self.state = ElevatorState.IDLE


class ElevatorVisualization:
    def __init__(self, num_floors=10):
        self.num_floors = num_floors
        self.elevator = Elevator(num_floors)
        
        # Создание GUI
        self.root = tk.Tk()
        self.root.title("Симулятор лифта (Алгоритм SCAN)")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Основной фрейм
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Верхняя панель с информацией
        info_frame = tk.Frame(main_frame, bg="lightgray", height=60)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        info_frame.pack_propagate(False)
        
        self.info_label = tk.Label(info_frame, text="", font=("Arial", 12, "bold"), bg="lightgray")
        self.info_label.pack(expand=True)
        
        # Панель с кнопками управления лифтом (внутренние кнопки)
        inside_frame = tk.Frame(main_frame, bg="lightblue", height=50)
        inside_frame.pack(fill=tk.X, pady=(0, 10))
        inside_frame.pack_propagate(False)
        
        tk.Label(inside_frame, text="Кнопки в лифте:", font=("Arial", 10, "bold"), 
                bg="lightblue").pack(side=tk.LEFT, padx=10)
        
        # Создаем кнопки этажей внутри лифта
        self.inside_buttons = {}
        button_frame = tk.Frame(inside_frame, bg="lightblue")
        button_frame.pack(side=tk.LEFT, padx=10)
        
        for floor in range(1, num_floors + 1):
            btn = tk.Button(button_frame, text=str(floor), width=3, height=1,
                          command=lambda f=floor: self.press_inside_button(f),
                          bg="white", relief=tk.RAISED)
            btn.pack(side=tk.LEFT, padx=2)
            self.inside_buttons[floor] = btn
        
        # Основная область с лифтом и этажами
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левый фрейм с этажами и кнопками вызова
        floors_frame = tk.Frame(content_frame, width=200)
        floors_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        floors_frame.pack_propagate(False)
        
        # Создаем панель для каждого этажа
        self.floor_frames = []
        self.up_buttons = {}
        self.down_buttons = {}
        
        for floor in range(num_floors, 0, -1):
            floor_panel = tk.Frame(floors_frame, relief=tk.RIDGE, bd=2)
            floor_panel.pack(fill=tk.X, pady=2)
            
            # Номер этажа
            tk.Label(floor_panel, text=f"Этаж {floor}:", font=("Arial", 10, "bold"),
                    width=8).pack(side=tk.LEFT, padx=5)
            
            # Кнопка вызова вверх (для всех этажей кроме последнего)
            if floor < num_floors:
                up_btn = tk.Button(floor_panel, text="↑", width=3, bg="lightgreen",
                                 command=lambda f=floor: self.call_elevator(f, Direction.UP))
                up_btn.pack(side=tk.LEFT, padx=2)
                self.up_buttons[floor] = up_btn
            else:
                tk.Label(floor_panel, text="  ", width=3).pack(side=tk.LEFT, padx=2)
            
            # Кнопка вызова вниз (для всех этажей кроме первого)
            if floor > 1:
                down_btn = tk.Button(floor_panel, text="↓", width=3, bg="lightcoral",
                                   command=lambda f=floor: self.call_elevator(f, Direction.DOWN))
                down_btn.pack(side=tk.LEFT, padx=2)
                self.down_buttons[floor] = down_btn
            else:
                tk.Label(floor_panel, text="  ", width=3).pack(side=tk.LEFT, padx=2)
            
            # Индикатор активного вызова
            indicator = tk.Label(floor_panel, text="", width=5, bg="white")
            indicator.pack(side=tk.LEFT, padx=5)
            
            self.floor_frames.append({
                'floor': floor,
                'panel': floor_panel,
                'indicator': indicator
            })
        
        # Центральный фрейм с холстом для лифта
        canvas_frame = tk.Frame(content_frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=1, 
                               highlightbackground="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Нижняя панель с очередью запросов
        queue_frame = tk.Frame(main_frame, bg="lightyellow", height=80)
        queue_frame.pack(fill=tk.X, pady=(10, 0))
        queue_frame.pack_propagate(False)
        
        tk.Label(queue_frame, text="Очередь запросов:", font=("Arial", 10, "bold"),
                bg="lightyellow").pack(anchor=tk.W, padx=10, pady=(5, 0))
        
        self.queue_label = tk.Label(queue_frame, text="", font=("Arial", 10),
                                   bg="lightyellow", wraplength=800)
        self.queue_label.pack(anchor=tk.W, padx=20, pady=(0, 5))
        
        # Запуск анимации
        self.last_time = time.time()
        self.update()
    
    def call_elevator(self, floor, direction):
        """Вызов лифта с этажа"""
        self.elevator.add_external_request(floor, direction)
    
    def press_inside_button(self, floor):
        """Нажатие кнопки внутри лифта"""
        self.elevator.add_internal_request(floor)
    
    def draw_elevator(self):
        """Отрисовка лифта и шахты"""
        self.canvas.delete("all")
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 100 or height < 100:
            return
        
        # Параметры отрисовки
        margin = 20
        shaft_width = width * 0.4
        shaft_x = (width - shaft_width) / 2
        
        # Рисуем шахту
        self.canvas.create_rectangle(shaft_x, margin, shaft_x + shaft_width, height - margin,
                                     outline="black", width=2, fill="white")
        
        # Вычисляем высоту этажа
        floor_height = (height - 2 * margin) / self.num_floors
        
        # Рисуем линии этажей
        for i in range(self.num_floors + 1):
            y = height - margin - i * floor_height
            self.canvas.create_line(shaft_x, y, shaft_x + shaft_width, y, fill="gray", width=1)
            
            # Номер этажа слева от шахты
            if i > 0:
                self.canvas.create_text(shaft_x - 15, y - floor_height/2,
                                       text=str(i), font=("Arial", 10, "bold"))
        
        # Рисуем кабину лифта
        # Позиция кабины (текущий этаж)
        cabin_y = height - margin - (self.elevator.current_floor - 0.5) * floor_height
        
        # Кабина
        cabin_height = floor_height * 0.8
        cabin_width = shaft_width * 0.8
        cabin_x = shaft_x + (shaft_width - cabin_width) / 2
        
        self.canvas.create_rectangle(cabin_x, cabin_y - cabin_height/2,
                                     cabin_x + cabin_width, cabin_y + cabin_height/2,
                                     fill="lightblue", outline="blue", width=2)
        
        # Двери
        door_width = cabin_width / 2 - 5
        
        if self.elevator.state == ElevatorState.DOOR_OPEN:
            # Открытые двери
            self.canvas.create_rectangle(cabin_x + 2, cabin_y - cabin_height/2 + 2,
                                        cabin_x + door_width, cabin_y + cabin_height/2 - 2,
                                        fill="saddle brown", outline="black")
            self.canvas.create_rectangle(cabin_x + cabin_width - door_width, cabin_y - cabin_height/2 + 2,
                                        cabin_x + cabin_width - 2, cabin_y + cabin_height/2 - 2,
                                        fill="saddle brown", outline="black")
        else:
            # Закрытые двери
            self.canvas.create_rectangle(cabin_x + 2, cabin_y - cabin_height/2 + 2,
                                        cabin_x + cabin_width - 2, cabin_y + cabin_height/2 - 2,
                                        fill="saddle brown", outline="black")
            # Линия между дверями
            self.canvas.create_line(cabin_x + cabin_width/2, cabin_y - cabin_height/2 + 2,
                                   cabin_x + cabin_width/2, cabin_y + cabin_height/2 - 2,
                                   fill="black", width=2)
        
        # Номер этажа на кабине
        self.canvas.create_text(cabin_x + cabin_width/2, cabin_y,
                               text=str(self.elevator.current_floor),
                               font=("Arial", 12, "bold"), fill="white")
        
        # Индикатор направления на кабине
        if self.elevator.direction == Direction.UP:
            self.canvas.create_text(cabin_x + cabin_width + 15, cabin_y,
                                   text="↑", font=("Arial", 16), fill="green")
        elif self.elevator.direction == Direction.DOWN:
            self.canvas.create_text(cabin_x + cabin_width + 15, cabin_y,
                                   text="↓", font=("Arial", 16), fill="red")
    
    def update_ui(self):
        """Обновление информации в UI"""
        # Информация о состоянии
        state_text = f"Текущий этаж: {self.elevator.current_floor} | Состояние: {self.elevator.state.value}"
        if self.elevator.direction != Direction.IDLE:
            state_text += f" | Направление: {'↑' if self.elevator.direction == Direction.UP else '↓'}"
        if self.elevator.target_floor:
            state_text += f" | Цель: {self.elevator.target_floor}"
        self.info_label.config(text=state_text)
        
        # Очередь запросов
        queue_text = " → ".join([str(f) for f in self.elevator.requests_queue]) if self.elevator.requests_queue else "Нет активных запросов"
        self.queue_label.config(text=queue_text)
        
        # Обновление индикаторов на этажах
        for floor_info in self.floor_frames:
            floor = floor_info['floor']
            indicator = floor_info['indicator']
            
            # Проверяем активные вызовы с этого этажа
            has_external = any(f == floor for f, _ in self.elevator.external_requests)
            
            if has_external:
                indicator.config(text="●", fg="red", bg="white")
            else:
                indicator.config(text="", bg="white")
            
            # Подсвечиваем кнопки вызова
            if floor in self.up_buttons:
                if (floor, Direction.UP) in self.elevator.external_requests:
                    self.up_buttons[floor].config(bg="yellow")
                else:
                    self.up_buttons[floor].config(bg="lightgreen")
            
            if floor in self.down_buttons:
                if (floor, Direction.DOWN) in self.elevator.external_requests:
                    self.down_buttons[floor].config(bg="yellow")
                else:
                    self.down_buttons[floor].config(bg="lightcoral")
        
        # Обновление кнопок внутри лифта
        for floor, btn in self.inside_buttons.items():
            if floor in self.elevator.internal_requests:
                btn.config(bg="yellow")
            else:
                btn.config(bg="white")
    
    def update(self):
        """Обновление анимации"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        # Ограничиваем dt для предотвращения рывков
        dt = min(dt, 0.1)
        
        # Обновляем состояние лифта
        self.elevator.update(dt)
        
        # Обновляем отображение
        self.draw_elevator()
        self.update_ui()
        
        # Планируем следующее обновление
        self.root.after(50, self.update)
    
    def run(self):
        """Запуск симуляции"""
        self.root.mainloop()


if __name__ == "__main__":
    # Создаем и запускаем визуализацию
    app = ElevatorVisualization(num_floors=10)
    app.run()
