import React, { useState } from "react";
import ChatCreate from '@/views/chat/components/chatCreate';

import { FaRegFileLines } from "react-icons/fa6";
import { FiAlertCircle } from "react-icons/fi";
import { FaCalendarCheck } from "react-icons/fa";
import { IoMdCheckmarkCircleOutline } from "react-icons/io";


const Home: React.FC = () => {
	const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)

	return (
		<>
			<div className="h-screen flex">
				<div className="flex-1 p-8 flex flex-col items-center justify-center max-w-4xl mx-auto">
					<div className="space-y-4 text-center max-w-2xl">
						<h2 className="text-xl font-bold text-gray-800 mb-4">
							<span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
								AI-Ассистент консультанта
							</span>
						</h2>

						<p className="text-center text-sm leading-relaxed text-gray-700">
							Это AI-Ассистент на базе <span className="font-semibold text-blue-700">LLM</span>, который анализирует и
							обрабатывает данные из разных источников в базе знаний и дает ответы на вопросы
						</p>

						<div className="bg-blue-50 p-3 rounded-lg border border-blue-100">
							<p className="text-center text-sm font-medium text-blue-800">
								После нажатия на кнопку "Начать работу" будет создано рабочее пространство, также вы сами можете создать
								рабочие пространства.
							</p>
						</div>

						<div className="flex items-start space-x-3 bg-gray-50 p-3 rounded-lg border border-gray-100">
							<FaRegFileLines className="h-5 w-5 text-gray-500 mt-0.5 flex-shrink-0" />
							<p className="text-left text-sm text-gray-700">
								<span className="font-medium text-gray-900">Рабочее пространство</span> - это корзина файлов, которые
								будут преобразованы в то, что LLM сможет понять и использовать в беседе. В рабочем пространстве вы можете
								<span className="font-medium text-green-700"> загрузить документ</span> и/или
								<span className="font-medium text-blue-700"> написать вопрос</span> в чат
							</p>
						</div>

						<p className="text-center text-sm italic text-gray-600">
							Ассистент отвечает на вопрос на основании информации из файлов, которые загружены в
							<span className="font-medium not-italic"> векторную базу</span>
						</p>

						<div className="bg-amber-50 p-4 rounded-lg border border-amber-100 my-2">
							<h3 className="text-sm font-bold text-amber-800 mb-2 flex items-center justify-center">
								<FiAlertCircle className="h-4 w-4 mr-1" />
								Рекомендации для получения качественных ответов
							</h3>

							<ul className="text-left space-y-2 text-sm text-amber-800">
								<li className="flex items-start">
									<FaCalendarCheck className="h-4 w-4 mr-2 mt-0.5 text-amber-600 flex-shrink-0" />
									<span>
										Указывать <span className="font-semibold">дату</span>, на которую вам нужна актуальная информация
									</span>
								</li>
								<li className="flex items-start">
									<IoMdCheckmarkCircleOutline className="h-4 w-4 mr-2 mt-0.5 text-amber-600 flex-shrink-0" />
									<span>
										Указывать <span className="font-semibold">ограничения по локации</span> при запросе
									</span>
								</li>
								<li className="flex items-start">
									<IoMdCheckmarkCircleOutline className="h-4 w-4 mr-2 mt-0.5 text-amber-600 flex-shrink-0" />
									<span>
										Если известно, в каком конкретном документе есть необходимая информация - можно{" "}
										<span className="font-semibold">указать этот документ</span> в запросе
									</span>
								</li>
								<li className="flex items-start">
									<IoMdCheckmarkCircleOutline className="h-4 w-4 mr-2 mt-0.5 text-amber-600 flex-shrink-0" />
									<span>
										При необходимости можно задавать <span className="font-semibold">форму ответа в виде таблицы</span>
									</span>
								</li>
							</ul>
						</div>

						<div className="pt-4">
							<button
								onClick={() => setIsCreateModalOpen(true)}
								className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 rounded-md hover:cursor-pointer">
								<span className="font-semibold text-base">Начать работу</span>
							</button>
						</div>
					</div>
				</div>
			</div>
			<ChatCreate opened={isCreateModalOpen} close={() => setIsCreateModalOpen(false)} />
		</>
	)
}

export default Home