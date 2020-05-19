{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import psycopg2 as pg\n",
    "import pandas.io.sql as psql\n",
    "import pandas as pd\n",
    "\n",
    "conn_str = \"host={0} port={1} dbname={2} user={3} password={4}\".format(\"localhost\", 5432, \"kanjidb\", \"postgres\", \"w0lfpack\")\n",
    "\n",
    "def kanjiDbConnect():\n",
    "  try:\n",
    "    conn = pg.connect(conn_str)\n",
    "    print(\"Welcome to Jupyter Notebook.  You are connected to the Kanji database!\")\n",
    "    return conn\n",
    "  except pg.OperationalError:\n",
    "    print(\"You are not connected to the database.\")\n",
    "    return None"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "KanjiProjects",
   "language": "python",
   "name": "kanjiprojects"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.2"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
